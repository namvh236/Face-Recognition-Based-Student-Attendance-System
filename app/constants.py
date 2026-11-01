"""Attendance status values. They are stored verbatim in Attendance.status,
so do not change them without migrating existing rows."""

STATUS_PRESENT = "Có mặt"
STATUS_ABSENT = "Vắng"
STATUS_PENDING = "Chưa điểm danh"

ALL_STATUSES = (STATUS_PRESENT, STATUS_ABSENT, STATUS_PENDING)
