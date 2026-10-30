"""One-time interactive bootstrap for the first administrator account."""

from getpass import getpass
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from pydantic import EmailStr, TypeAdapter, ValidationError

from app.services.auth_service import auth_service


def main() -> int:
    try:
        email = str(TypeAdapter(EmailStr).validate_python(input("Admin email: ").strip()))
        name = input("Admin full name: ").strip()
        password = getpass("Admin password (minimum 10 characters): ")
        if len(password) < 10:
            print("Password must be at least 10 characters.")
            return 1
        confirmation = getpass("Confirm password: ")
        if password != confirmation:
            print("Passwords do not match.")
            return 1
        if not name:
            print("Name is required.")
            return 1
        if not auth_service.create_first_admin(email=email, full_name=name, password=password):
            print("An administrator already exists; no account was created.")
            return 1
        print("First administrator created. Sign in through the application.")
        return 0
    except (ValueError, ValidationError) as exc:
        print(f"Unable to initialize administrator: {exc}")
        return 1
    except (KeyboardInterrupt, EOFError):
        print("Administrator initialization cancelled.")
        return 1
    except Exception:
        print("Unable to initialize administrator. Check database connectivity and migrations.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
