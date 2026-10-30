"""Deterministic identities for development-only seeded faculty accounts."""

from uuid import UUID

DEV_FACULTY_IDS = {
    "academic.faculty@sqm.local": UUID("00000000-0000-4000-8000-000000000001"),
    "exam.faculty@sqm.local": UUID("00000000-0000-4000-8000-000000000002"),
    "attendance.faculty@sqm.local": UUID("00000000-0000-4000-8000-000000000003"),
    "fees.faculty@sqm.local": UUID("00000000-0000-4000-8000-000000000004"),
    "technical.faculty@sqm.local": UUID("00000000-0000-4000-8000-000000000005"),
}

DEFAULT_CATEGORIES = (
    ("Academic", "Course content, instruction, and academic guidance.", "academic.faculty@sqm.local"),
    ("Examination", "Exam schedules, results, and examination concerns.", "exam.faculty@sqm.local"),
    ("Attendance", "Attendance records and attendance requirements.", "attendance.faculty@sqm.local"),
    ("Fees", "Tuition, payments, and fee-related questions.", "fees.faculty@sqm.local"),
    ("Technical", "Technical issues with university systems.", "technical.faculty@sqm.local"),
    ("Other", "Queries that do not fit another category.", "academic.faculty@sqm.local"),
)
