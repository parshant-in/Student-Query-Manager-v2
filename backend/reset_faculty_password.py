"""Deprecated manual password-reset entry point.

Password resets are now audited and available only to authenticated administrators
through the Admin Dashboard.
"""

raise SystemExit(
    "Direct password reset is disabled. Sign in as an administrator and use the Admin Dashboard."
)
