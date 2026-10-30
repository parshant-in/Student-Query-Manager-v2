from __future__ import annotations

import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.models.query import Category
from app.models.user import User, UserRole
from app.routes import admin as admin_routes
from app.core.security import verify_password
from app.routes import auth as auth_routes
from app.routes.auth import get_current_user
from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService, DuplicateEmailError, InvalidCredentialsError
from app.services.admin_service import AdminService


class MemoryUsers:
    def __init__(self):
        self.by_id = {}
        self.by_email = {}
        self.first_admin_created = False
        self.password_reset_events = []

    def get_by_email(self, email):
        return self.by_email.get(email.casefold())

    def get_by_id(self, user_id):
        return self.by_id.get(user_id)

    def add(self, user):
        if user.email in self.by_email:
            raise ValueError("duplicate")
        self.by_id[user.id] = user
        self.by_email[user.email] = user

    def create_first_admin(self, user):
        if self.first_admin_created:
            return False
        self.first_admin_created = True
        self.add(user)
        return True

    def create_faculty(self, user, department_id):
        self.add(user)

    def list_by_role(self, role):
        return [user for user in self.by_id.values() if user.role == role]

    def set_active(self, user_id, is_active):
        user = self.by_id.get(user_id)
        if not user or user.role != UserRole.faculty:
            return False
        user.is_active = is_active
        return True

    def set_faculty_department(self, user_id, department_id):
        user = self.by_id.get(user_id)
        if not user or user.role != UserRole.faculty:
            return False
        user.department_id = department_id
        return True

    def reset_password(self, *, user_id, admin_id, password_hash):
        user = self.by_id.get(user_id)
        if not user or user.role not in {UserRole.student, UserRole.faculty}:
            return None
        user.password_hash = password_hash
        user.token_version += 1
        self.password_reset_events.append((user_id, admin_id, user.role))
        return user


class MemoryCategories:
    def __init__(self, category):
        self.category = category

    def get_by_id(self, category_id):
        return self.category if self.category.id == category_id else None


class AdminAccountTests(unittest.TestCase):
    def setUp(self):
        self.department_id = uuid4()
        self.users = MemoryUsers()
        self.category = Category(self.department_id, "Fees", "Fee support", uuid4())
        self.admin_service = AdminService(self.users, MemoryCategories(self.category))

    def test_first_admin_can_only_be_bootstrapped_once(self):
        auth = AuthService(self.users)
        self.assertTrue(auth.create_first_admin(
            email="admin@example.test", full_name="First Admin", password="strong-password"
        ))
        self.assertFalse(auth.create_first_admin(
            email="second@example.test", full_name="Second Admin", password="strong-password"
        ))
        self.assertEqual(1, len(self.users.list_by_role(UserRole.admin)))

    def test_faculty_creation_assigns_department_and_status_can_disable_login(self):
        faculty = self.admin_service.create_faculty(
            email="faculty@example.test", full_name="Faculty Member",
            password="strong-password", department_id=self.department_id,
        )
        self.assertEqual(self.department_id, faculty.department_id)
        account = self.admin_service.set_faculty_status(faculty.id, False)
        self.assertFalse(account.is_active)
        with self.assertRaises(InvalidCredentialsError):
            AuthService(self.users).login(email=faculty.email, password="strong-password")

    def test_unknown_department_is_rejected(self):
        with self.assertRaises(LookupError):
            self.admin_service.create_faculty(
                email="faculty@example.test", full_name="Faculty Member",
                password="strong-password", department_id=uuid4(),
            )

    def test_public_registration_schema_rejects_role_escalation(self):
        with self.assertRaises(ValidationError):
            RegisterRequest(
                email="student@example.test", full_name="Student",
                password="strong-password", role="admin",
            )

    def test_every_admin_faculty_endpoint_rejects_non_admin_roles(self):
        app = FastAPI()
        app.include_router(admin_routes.router, prefix="/api")
        client = TestClient(app)
        for role in (UserRole.student, UserRole.faculty):
            user = User(uuid4(), f"{role.value}@example.test", role.value, role, "hash", datetime.now(timezone.utc))
            app.dependency_overrides[get_current_user] = lambda user=user: user
            self.assertEqual(403, client.get("/api/admin/faculty").status_code)
            self.assertEqual(403, client.get("/api/admin/students").status_code)
            self.assertEqual(403, client.post("/api/admin/faculty", json={
                "email": "new@example.test", "full_name": "New Faculty",
                "password": "strong-password", "department_id": str(self.department_id),
            }).status_code)
            self.assertEqual(403, client.patch(f"/api/admin/faculty/{uuid4()}/status", json={
                "is_active": False,
            }).status_code)
            self.assertEqual(403, client.patch(f"/api/admin/faculty/{uuid4()}/department", json={
                "department_id": str(self.department_id),
            }).status_code)

    def test_admin_can_create_faculty_with_department(self):
        app = FastAPI()
        app.include_router(admin_routes.router, prefix="/api")
        app.dependency_overrides[get_current_user] = lambda: User(
            uuid4(), "admin@example.test", "Admin", UserRole.admin, "hash", datetime.now(timezone.utc)
        )
        with patch.object(admin_routes, "admin_service", self.admin_service):
            response = TestClient(app).post("/api/admin/faculty", json={
                "email": "new-faculty@example.com", "full_name": "New Faculty",
                "password": "strong-password", "department_id": str(self.department_id),
            })
        self.assertEqual(201, response.status_code)
        self.assertEqual(str(self.department_id), response.json()["department_id"])
        self.assertEqual("faculty", response.json()["role"])

    def test_admin_can_reset_student_password_without_changing_other_accounts(self):
        auth = AuthService(self.users)
        _, student = auth.register(email="student@example.test", full_name="Student", password="old-password")
        _, other_student = auth.register(email="other@example.test", full_name="Other", password="other-password")
        admin_id = uuid4()
        reset = self.admin_service.reset_user_password(
            user_id=student.id, admin_id=admin_id, new_password="new-password"
        )
        self.assertEqual(student.id, reset.id)
        self.assertTrue(verify_password("new-password", self.users.get_by_id(student.id).password_hash))
        self.assertFalse(verify_password("old-password", self.users.get_by_id(student.id).password_hash))
        self.assertTrue(verify_password("other-password", self.users.get_by_id(other_student.id).password_hash))
        self.assertEqual(1, self.users.get_by_id(student.id).token_version)
        self.assertEqual([(student.id, admin_id, UserRole.student)], self.users.password_reset_events)

    def test_admin_can_reset_faculty_password_and_old_password_stops_working(self):
        faculty = self.admin_service.create_faculty(
            email="faculty-reset@example.test", full_name="Faculty Member",
            password="old-password", department_id=self.department_id,
        )
        self.admin_service.reset_user_password(
            user_id=faculty.id, admin_id=uuid4(), new_password="new-password"
        )
        with self.assertRaises(InvalidCredentialsError):
            AuthService(self.users).login(email=faculty.email, password="old-password")
        _, logged_in = AuthService(self.users).login(email=faculty.email, password="new-password")
        self.assertEqual(faculty.id, logged_in.id)

    def test_password_reset_revokes_existing_access_token(self):
        auth = AuthService(self.users)
        old_token, student = auth.register(
            email="token-student@example.test", full_name="Student", password="old-password"
        )
        self.admin_service.reset_user_password(
            user_id=student.id, admin_id=uuid4(), new_password="new-password"
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=old_token)
        with patch.object(auth_routes, "auth_service", auth):
            with self.assertRaises(HTTPException) as raised:
                auth_routes.get_current_user(credentials)
        self.assertEqual(401, raised.exception.status_code)

    def test_reset_endpoint_rejects_unauthenticated_and_non_admin_users(self):
        app = FastAPI()
        app.include_router(admin_routes.router, prefix="/api")
        client = TestClient(app)
        target_id = uuid4()
        self.assertEqual(401, client.post(f"/api/admin/users/{target_id}/reset-password", json={"new_password": "new-password"}).status_code)
        for role in (UserRole.student, UserRole.faculty):
            app.dependency_overrides[get_current_user] = lambda role=role: User(
                uuid4(), f"{role.value}@example.test", role.value, role, "hash", datetime.now(timezone.utc)
            )
            self.assertEqual(403, client.post(f"/api/admin/users/{target_id}/reset-password", json={"new_password": "new-password"}).status_code)

    def test_reset_endpoint_returns_404_for_unknown_or_admin_accounts(self):
        app = FastAPI()
        app.include_router(admin_routes.router, prefix="/api")
        app.dependency_overrides[get_current_user] = lambda: User(
            uuid4(), "admin@example.test", "Admin", UserRole.admin, "hash", datetime.now(timezone.utc)
        )
        with patch.object(admin_routes, "admin_service", self.admin_service):
            client = TestClient(app)
            self.assertEqual(404, client.post(f"/api/admin/users/{uuid4()}/reset-password", json={"new_password": "new-password"}).status_code)
            admin = User(uuid4(), "another-admin@example.test", "Admin", UserRole.admin, "hash", datetime.now(timezone.utc))
            self.users.add(admin)
            self.assertEqual(404, client.post(f"/api/admin/users/{admin.id}/reset-password", json={"new_password": "new-password"}).status_code)

    def test_reset_endpoint_rejects_invalid_password_input(self):
        app = FastAPI()
        app.include_router(admin_routes.router, prefix="/api")
        app.dependency_overrides[get_current_user] = lambda: User(
            uuid4(), "admin@example.test", "Admin", UserRole.admin, "hash", datetime.now(timezone.utc)
        )
        response = TestClient(app).post(f"/api/admin/users/{uuid4()}/reset-password", json={"new_password": "short"})
        self.assertEqual(422, response.status_code)

    def test_admin_reset_endpoint_updates_selected_student(self):
        _, student = AuthService(self.users).register(
            email="endpoint-student@example.test", full_name="Student", password="old-password"
        )
        admin_id = uuid4()
        app = FastAPI()
        app.include_router(admin_routes.router, prefix="/api")
        app.dependency_overrides[get_current_user] = lambda: User(
            admin_id, "admin@example.test", "Admin", UserRole.admin, "hash", datetime.now(timezone.utc)
        )
        with patch.object(admin_routes, "admin_service", self.admin_service):
            response = TestClient(app).post(
                f"/api/admin/users/{student.id}/reset-password", json={"new_password": "new-password"}
            )
        self.assertEqual(200, response.status_code)
        self.assertEqual(str(student.id), response.json()["id"])
        self.assertTrue(verify_password("new-password", self.users.get_by_id(student.id).password_hash))


if __name__ == "__main__":
    unittest.main()
