"""Giá trị trạng thái điểm danh. Được lưu trực tiếp vào DB (Attendance.status)
nên KHÔNG đổi giá trị nếu không migrate dữ liệu cũ."""

STATUS_PRESENT = "Có mặt"
STATUS_ABSENT = "Vắng"
STATUS_PENDING = "Chưa điểm danh"

ALL_STATUSES = (STATUS_PRESENT, STATUS_ABSENT, STATUS_PENDING)
