"""Legacy command retained to direct operators to the protected admin workflow."""

import sys


def main() -> int:
    print("Direct faculty creation is disabled. Sign in as an administrator and use the Admin Dashboard.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
