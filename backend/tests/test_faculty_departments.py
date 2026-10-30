from __future__ import annotations

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.orm_models import CategoryRecord, QueryRecord, UserRecord
from app.models.query import Category, Query, QueryStatus
from app.models.user import User, UserRole
from app.repositories.query_repository import QueryRepository
from app.routes.faculty import get_current_faculty
from app.routes.auth import get_current_user
from app.routes import faculty as faculty_routes
from app.models.response import FacultyResponse
from app.services.query_service import QueryAlreadyClaimedError, QueryService


class FakeCategories:
    def __init__(self, category: Category) -> None:
        self.category = category

    def get_by_id(self, category_id):
        return self.category if category_id == self.category.id else None


class FakeUsers:
    def __init__(self) -> None:
        self.departments = {}

    def get_department_id(self, user_id):
        return self.departments.get(user_id)


class FakeQueries:
    def __init__(self) -> None:
        self.records = {}

    def add(self, query):
        self.records[query.id] = query

    def get_by_id(self, query_id):
        return self.records.get(query_id)

    def list_for_faculty_department(self, _faculty_id, department_id):
        return [q for q in self.records.values() if q.category_id == department_id]

    def claim_for_faculty(self, query_id, faculty_id, department_id):
        query = self.records.get(query_id)
        if query is None or query.category_id != department_id or query.faculty_id is not None:
            return False
        query.faculty_id = faculty_id
        return True

    def add_response(self, response, *, query_updated_at):
        query = self.records[response.query_id]
        query.responses.append(response)
        query.updated_at = query_updated_at
        return True

    def update_status(self, query, *, faculty_id):
        stored = self.records.get(query.id)
        if stored is None or stored.faculty_id != faculty_id:
            return False
        stored.status = query.status
        stored.updated_at = query.updated_at
        return True


class FacultyDepartmentTests(unittest.TestCase):
    def setUp(self):
        self.department_id = uuid4()
        self.student_id = uuid4()
        self.faculty_a = uuid4()
        self.faculty_b = uuid4()
        self.category = Category(self.department_id, "Fees", "Fee queries", self.faculty_a)
        self.users = FakeUsers()
        self.queries = FakeQueries()
        self.service = QueryService(FakeCategories(self.category), self.queries, self.users)

    def test_faculty_in_same_department_see_department_queries(self):
        self.users.departments[self.faculty_a] = self.department_id
        self.users.departments[self.faculty_b] = self.department_id
        query = self.service.create_query(
            student_id=self.student_id,
            category_id=self.department_id,
            title="Fee receipt",
            description="Please check this payment.",
        )
        self.assertIsNone(query.faculty_id)
        self.assertEqual([query], self.service.list_faculty_queries(self.faculty_a))
        self.assertEqual([query], self.service.list_faculty_queries(self.faculty_b))

    def test_only_one_faculty_can_claim_and_only_owner_can_respond(self):
        self.users.departments[self.faculty_a] = self.department_id
        self.users.departments[self.faculty_b] = self.department_id
        query = self.service.create_query(
            student_id=self.student_id,
            category_id=self.department_id,
            title="Fee receipt",
            description="Please check this payment.",
        )
        self.assertEqual(query, self.service.claim_faculty_query(self.faculty_a, query.id))
        with self.assertRaises(QueryAlreadyClaimedError):
            self.service.claim_faculty_query(self.faculty_b, query.id)
        self.assertIsNone(self.service.add_faculty_response(
            faculty_id=self.faculty_b, query_id=query.id, message="Not my claim"
        ))
        self.assertIsNotNone(self.service.add_faculty_response(
            faculty_id=self.faculty_a, query_id=query.id, message="I can help"
        ))

    def test_faculty_outside_department_cannot_claim(self):
        outside_faculty = uuid4()
        self.users.departments[self.faculty_a] = self.department_id
        self.users.departments[outside_faculty] = uuid4()
        query = self.service.create_query(
            student_id=self.student_id, category_id=self.department_id,
            title="Fee receipt", description="Please check this payment.",
        )
        self.assertIsNone(self.service.claim_faculty_query(outside_faculty, query.id))
        self.assertIsNone(query.faculty_id)

    def test_only_owner_can_change_status(self):
        self.users.departments[self.faculty_a] = self.department_id
        self.users.departments[self.faculty_b] = self.department_id
        query = self.service.create_query(
            student_id=self.student_id, category_id=self.department_id,
            title="Fee receipt", description="Please check this payment.",
        )
        self.service.claim_faculty_query(self.faculty_a, query.id)
        self.assertIsNone(self.service.update_status(
            faculty_id=self.faculty_b, query_id=query.id, status=QueryStatus.solved
        ))
        self.assertEqual(QueryStatus.pending, query.status)
        self.assertEqual(QueryStatus.solved, self.service.update_status(
            faculty_id=self.faculty_a, query_id=query.id, status=QueryStatus.solved
        ).status)

    def test_legacy_assigned_query_is_visible_to_department_but_remains_owned(self):
        self.users.departments[self.faculty_a] = self.department_id
        self.users.departments[self.faculty_b] = self.department_id
        legacy_query = Query(
            id=uuid4(), student_id=self.student_id, category_id=self.department_id,
            faculty_id=self.faculty_a, title="Older fee question", description="Pending",
            status=QueryStatus.pending, created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc), responses=[],
        )
        self.queries.add(legacy_query)

        self.assertEqual([legacy_query], self.service.list_faculty_queries(self.faculty_b))
        self.assertEqual(legacy_query, self.service.get_faculty_query(self.faculty_b, legacy_query.id))
        with self.assertRaises(QueryAlreadyClaimedError):
            self.service.claim_faculty_query(self.faculty_b, legacy_query.id)
        self.assertIsNone(self.service.add_faculty_response(
            faculty_id=self.faculty_b, query_id=legacy_query.id, message="Not the owner"
        ))
        self.assertEqual([], legacy_query.responses)

    def test_student_role_is_rejected_by_faculty_guard(self):
        student = User(uuid4(), "student@example.edu", "Student", UserRole.student, "hash", datetime.now(timezone.utc))
        with self.assertRaises(HTTPException) as raised:
            get_current_faculty(student)
        self.assertEqual(403, raised.exception.status_code)

    def test_student_cannot_access_faculty_department_or_claim_endpoints(self):
        app = FastAPI()
        app.include_router(faculty_routes.router, prefix="/api")
        app.include_router(faculty_routes.department_router, prefix="/api")
        app.dependency_overrides[get_current_user] = lambda: User(
            uuid4(), "student@example.edu", "Student", UserRole.student, "hash", datetime.now(timezone.utc)
        )
        client = TestClient(app)
        self.assertEqual(403, client.get("/api/faculty/department").status_code)
        self.assertEqual(405, client.put(
            "/api/faculty/department", json={"department_id": str(self.department_id)}
        ).status_code)
        self.assertEqual(403, client.post(f"/api/faculty/queries/{uuid4()}/claim").status_code)

    def test_database_claim_is_conditional_and_exclusive(self):
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        try:
            Base.metadata.create_all(engine)
            sessions = sessionmaker(bind=engine, expire_on_commit=False)
            now = datetime.now(timezone.utc)
            with sessions() as session:
                session.add_all([
                    UserRecord(id=self.student_id, email="student@test.local", full_name="Student", password_hash="x", role="student", created_at=now),
                    UserRecord(id=self.faculty_a, email="faculty-a@test.local", full_name="Faculty A", password_hash="x", role="faculty", created_at=now),
                    UserRecord(id=self.faculty_b, email="faculty-b@test.local", full_name="Faculty B", password_hash="x", role="faculty", created_at=now),
                    CategoryRecord(id=self.department_id, name="Fees test", description="Test department", faculty_id=self.faculty_a),
                ])
                session.add(QueryRecord(
                    id=(query_id := uuid4()), student_id=self.student_id, category_id=self.department_id,
                    faculty_id=None, title="Test query", description="Details", status="pending",
                    created_at=now, updated_at=now,
                ))
                session.add(QueryRecord(
                    id=(legacy_query_id := uuid4()), student_id=self.student_id, category_id=self.department_id,
                    faculty_id=self.faculty_a, title="Legacy query", description="Older details", status="pending",
                    created_at=now, updated_at=now,
                ))
                session.commit()
            with patch("app.repositories.query_repository.SessionLocal", sessions):
                repository = QueryRepository()
                department_queries = repository.list_for_faculty_department(self.faculty_b, self.department_id)
                self.assertIn(legacy_query_id, {q.id for q in department_queries})
                with ThreadPoolExecutor(max_workers=2) as pool:
                    results = list(pool.map(
                        lambda faculty_id: repository.claim_for_faculty(
                            query_id, faculty_id, self.department_id
                        ),
                        (self.faculty_a, self.faculty_b),
                    ))
                self.assertEqual(1, sum(results))
            with sessions() as session:
                stored = session.scalar(select(QueryRecord).where(QueryRecord.id == query_id))
                self.assertIn(stored.faculty_id, {self.faculty_a, self.faculty_b})
                owner_id = stored.faculty_id
            with patch("app.repositories.query_repository.SessionLocal", sessions):
                response = FacultyResponse(
                    id=uuid4(), query_id=query_id, faculty_id=owner_id,
                    message="We have reviewed this request.", created_at=now,
                )
                intruder_response = FacultyResponse(
                    id=uuid4(), query_id=query_id,
                    faculty_id=self.faculty_b if owner_id == self.faculty_a else self.faculty_a,
                    message="Unauthorized response", created_at=now,
                )
                self.assertFalse(repository.add_response(intruder_response, query_updated_at=now))
                self.assertTrue(repository.add_response(response, query_updated_at=now))
                claimed = repository.get_by_id(query_id)
                claimed.status = QueryStatus.solved
                claimed.updated_at = now
                self.assertTrue(repository.update_status(claimed, faculty_id=owner_id))
            with sessions() as session:
                stored = session.scalar(select(QueryRecord).where(QueryRecord.id == query_id))
                self.assertEqual("solved", stored.status)
                self.assertEqual(1, len(stored.responses))
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
