from datetime import datetime

from app.config import ENROLLED_FACES_DIR
from app.constants import STATUS_PENDING, STATUS_PRESENT
from app.database.connector import get_session
from app.database.models import Course, Student, Attendance, User
from app.services.face_service import (
    embeddings_from_dir, enroll_face, get_face_embedding, load_cache, save_cache,
)

NO_TIME = "--:--"


def _now():
    return datetime.now().strftime("%H:%M:%S")


def get_teacher_detail(teacher_id):
    """Return the teacher's User row (phone, email, ...)."""
    session = get_session()
    try:
        teacher = session.get(User, teacher_id)
        if teacher:
            session.expunge(teacher)
        return teacher
    finally:
        session.close()


def get_teaching_stats(teacher_id):
    """List the teacher's courses with student counts."""
    session = get_session()
    try:
        courses = session.query(Course).filter_by(teacher_id=teacher_id).all()
        return [{
            "code": c.course_code,
            "name": c.course_name,
            "count": session.query(Student).filter_by(course_id=c.id).count(),
        } for c in courses]
    finally:
        session.close()


def load_known_faces(course_id):
    """
    Merge DB students with the face cache for one course.
    Returns (embeddings, mssv_list, name_list).
    """
    print(f"Loading face data for course {course_id}...")

    session = get_session()
    try:
        students = session.query(Student).filter_by(course_id=course_id).all()
        names_by_mssv = {s.mssv: s.name for s in students}
    finally:
        session.close()

    cached_data = load_cache()
    if not cached_data:
        print("Face cache is empty, rebuilding from enrolled photos...")
        cached_data = embeddings_from_dir(ENROLLED_FACES_DIR)
        save_cache(cached_data)

    known_embeddings, known_mssvs, known_names = [], [], []
    for mssv, embedding in cached_data.items():
        if mssv in names_by_mssv:
            known_embeddings.append(embedding)
            known_mssvs.append(mssv)
            known_names.append(names_by_mssv[mssv])

    print(f"Loaded {len(known_mssvs)} faces for this course.")
    return known_embeddings, known_mssvs, known_names


def get_teacher_courses(teacher_id):
    session = get_session()
    try:
        courses = session.query(Course).filter_by(teacher_id=teacher_id).all()
        session.expunge_all()
        return courses
    finally:
        session.close()


def get_attendance_list(course_id, date_str):
    session = get_session()
    try:
        students = session.query(Student).filter_by(course_id=course_id).all()
        attendance_by_student = {
            a.student_id: a
            for a in session.query(Attendance).filter_by(course_id=course_id, date=date_str)
        }

        result = []
        for s in students:
            att = attendance_by_student.get(s.id)
            result.append({
                "id": s.id,
                "mssv": s.mssv,
                "name": s.name or "",
                "dob": str(s.dob) if s.dob else "",
                "class_name": s.class_name or "",
                "status": att.status if att else STATUS_PENDING,
                "time": att.time if att else NO_TIME,
                "note": (att.note if att else None) or "",
            })
        return result
    finally:
        session.close()


def _get_or_create_attendance(session, mssv, course_id, date_str):
    """Return the Attendance row for the student/day, creating a pending one if needed.

    Returns None if the MSSV is not enrolled in the course.
    """
    student = session.query(Student).filter_by(mssv=mssv, course_id=course_id).first()
    if not student:
        print(f"Student {mssv} not found in course {course_id}")
        return None

    att = session.query(Attendance).filter_by(student_id=student.id, course_id=course_id, date=date_str).first()
    if att is None:
        att = Attendance(student_id=student.id, course_id=course_id, date=date_str,
                         time=NO_TIME, status=STATUS_PENDING)
        session.add(att)
    return att


def update_attendance(mssv, course_id, date_str, status):
    """Set the student's status for the day. Returns False if the student is not in the course."""
    session = get_session()
    try:
        att = _get_or_create_attendance(session, mssv, course_id, date_str)
        if att is None:
            return False

        if att.status != status:
            att.status = status
            att.time = _now() if status == STATUS_PRESENT else NO_TIME
            session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_note(mssv, course_id, date_str, note):
    """Save the teacher's note for the student's attendance of the day."""
    session = get_session()
    try:
        att = _get_or_create_attendance(session, mssv, course_id, date_str)
        if att is None:
            return False
        att.note = note.strip() or None
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def add_student(mssv, name, dob, class_name, course_id, frame):
    """
    Enroll a student's face, creating the student if needed:
    1. Reject the photo if it contains no face.
    2. Insert the DB row (or reuse the existing row of this course, e.g. imported from Excel).
    3. Save the photo and update the embedding cache so recognition works immediately.
    """
    embedding = get_face_embedding(frame)
    if embedding is None:
        return False, "Không tìm thấy khuôn mặt trong ảnh, vui lòng chụp lại!"

    session = get_session()
    try:
        existing = session.query(Student).filter_by(mssv=mssv).first()
        if existing and existing.course_id != course_id:
            return False, f"MSSV {mssv} đã thuộc một lớp khác."

        if existing:
            message = "Đã cập nhật ảnh khuôn mặt cho sinh viên."
        else:
            session.add(Student(mssv=mssv, name=name, dob=dob, class_name=class_name, course_id=course_id))
            message = "Thêm sinh viên thành công!"

        enroll_face(mssv, frame, embedding)
        session.commit()
        return True, message
    except Exception as e:
        session.rollback()
        return False, f"Lỗi: {e}"
    finally:
        session.close()


def import_student_from_excel(mssv, name, dob, class_name, course_id):
    session = get_session()
    try:
        existing = session.query(Student).filter_by(mssv=mssv).first()
        if existing:
            if existing.course_id == course_id:
                return False, f"MSSV {mssv} đã tồn tại trong lớp."
            return False, f"MSSV {mssv} đã thuộc một lớp khác."

        session.add(Student(mssv=mssv, name=name, dob=dob, class_name=class_name, course_id=course_id))
        session.commit()
        return True, "Thành công"
    except Exception as e:
        session.rollback()
        return False, f"Lỗi Data: {e}"
    finally:
        session.close()


def create_or_get_course(course_code, course_name, teacher_id):
    session = get_session()
    try:
        course = session.query(Course).filter_by(course_code=course_code, teacher_id=teacher_id).first()
        if not course:
            course = Course(course_code=course_code, course_name=course_name, teacher_id=teacher_id, credits=3)
            session.add(course)
            session.commit()
            session.refresh(course)
        return course.id
    finally:
        session.close()
