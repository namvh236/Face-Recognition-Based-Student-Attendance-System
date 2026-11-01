from dataclasses import dataclass
from typing import Optional

from app.database.connector import get_session
from app.database.models import Student, Attendance, User, Course

NO_TEACHER_NAME = "Chưa cập nhật"
NO_TEACHER_PHONE = "Chưa có SĐT"


@dataclass
class UnenrolledStudent:
    """Stand-in for a student account that has no Student row yet (not on any class roster)."""
    name: str
    mssv: str
    email: Optional[str] = None
    id: Optional[int] = None
    dob: Optional[object] = None
    class_name: Optional[str] = None


def get_student_by_user_id(user_id):
    """Return the Student for a login account.

    The first sign-in links the account to the roster row with the same MSSV. Accounts that match
    no roster row get an `UnenrolledStudent` placeholder, or None if the user does not exist.
    """
    session = get_session()
    try:
        student = session.query(Student).filter_by(user_id=user_id).first()

        if student is None:
            user = session.get(User, user_id)
            if user is None:
                return None
            student = session.query(Student).filter_by(mssv=user.user_code, user_id=None).first()
            if student is None:
                return UnenrolledStudent(name=user.fullname, mssv=user.user_code, email=user.email)
            student.user_id = user.id
            session.commit()
            session.refresh(student)

        session.expunge(student)
        return student
    finally:
        session.close()


def get_student_course_details(student_id):
    """List the student's courses with teacher info (at most one: `Student.mssv` is unique)."""
    if student_id is None:
        return []
    session = get_session()
    try:
        student = session.get(Student, student_id)
        if not student or not student.course:
            return []

        course = student.course
        teacher = course.teacher
        return [{
            "course_id": course.id,
            "course_name": course.course_name,
            "course_code": course.course_code,
            "teacher_name": (teacher.fullname if teacher else None) or NO_TEACHER_NAME,
            "teacher_phone": (teacher.phone_number if teacher else None) or NO_TEACHER_PHONE,
        }]
    finally:
        session.close()


def get_student_attendance_history(student_id, course_id):
    if student_id is None:
        return []
    session = get_session()
    try:
        course = session.get(Course, course_id)
        teacher = course.teacher if course else None
        teacher_name = (teacher.fullname if teacher else None) or NO_TEACHER_NAME
        teacher_phone = (teacher.phone_number if teacher else None) or NO_TEACHER_PHONE

        attendances = (session.query(Attendance)
                       .filter_by(student_id=student_id, course_id=course_id)
                       .order_by(Attendance.date.desc())
                       .all())

        return [{
            "date": a.date,
            "time": a.time,
            "status": a.status,
            "note": a.note or "",
            "teacher_name": teacher_name,
            "teacher_phone": teacher_phone,
        } for a in attendances]
    finally:
        session.close()
