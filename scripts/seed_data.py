"""Seed sample teachers, courses and students. Run from the repo root: python -m scripts.seed_data"""
import os
import random
from datetime import date, timedelta

from app.config import RAW_FACES_DIR
from app.database.connector import init_db, get_session
from app.database.models import User, Course, Student

# Sample data
HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
DEM = ["Văn", "Thị", "Minh", "Đức", "Ngọc", "Xuân", "Thanh", "Hữu", "Gia", "Khánh", "Tuấn", "Hoài", "Quốc", "Mạnh", "Thùy", "Phương"]
TEN = ["Anh", "Bảo", "Châu", "Dũng", "Em", "Giang", "Hà", "Hải", "Hiếu", "Hòa", "Hùng", "Huy", "Khánh", "Khoa", "Lâm", "Linh", "Long", "Minh", "Nam", "Nga", "Nhi", "Phát", "Phúc", "Quân", "Quỳnh", "Sơn", "Thảo", "Thắng", "Thịnh", "Trang", "Trung", "Tú", "Tùng", "Việt", "Vinh", "Uyên", "Yến"]

CLASSES_ADMIN = ["DCCTCT67A", "DCCTCT67B"]


def generate_random_name():
    return f"{random.choice(HO)} {random.choice(DEM)} {random.choice(TEN)}"

def get_random_dob_2004():
    start_date = date(2004, 1, 1)
    end_date = date(2004, 12, 31)
    return start_date + timedelta(days=random.randrange((end_date - start_date).days))

def generate_phone():
    """Random Vietnamese mobile number for a teacher."""
    prefixes = ["090", "091", "098", "097", "089"]
    suffix = "".join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{random.choice(prefixes)}{suffix}"

def check_student_avatar(mssv):
    """Return the repo-relative path of data/raw_faces/<mssv>.(jpg|png|jpeg) if it exists, else None."""
    if not os.path.exists(RAW_FACES_DIR):
        return None
        
    extensions = [".jpg", ".png", ".jpeg"]
    
    for ext in extensions:
        file_name = f"{mssv}{ext}"
        full_path = os.path.join(RAW_FACES_DIR, file_name)
        
        if os.path.exists(full_path):
            # Stored relative to the repo root, e.g. data/raw_faces/9900000001.jpg
            return f"data/raw_faces/{file_name}"
            
    return None

def seed():
    print("Initializing database...")
    
    # Ensure raw_faces exists so the avatar lookup below cannot fail
    if not os.path.exists(RAW_FACES_DIR):
        os.makedirs(RAW_FACES_DIR)
        print(f"Created empty directory {RAW_FACES_DIR}. Put <mssv>.jpg photos there to link avatars.")

    init_db() 
    session = get_session()

    # 1. Teachers
    print("Creating Teachers...")
    teachers_data = [
        {
            "u": "admin", 
            "n": "Teacher One", 
            "c": "GV001", 
            "email": "teacher1@example.com",
            "avt": "assets/img/teacher/gv001.jpg"
        },
        {
            "u": "gv002", 
            "n": "Teacher Two", 
            "c": "GV002", 
            "email": "teacher2@example.com",
            "avt": "assets/img/teacher/gv002.jpg"
        }
    ]

    for t in teachers_data:
        if not session.query(User).filter_by(username=t["u"]).first():
            gv = User(
                username=t["u"], password="123", fullname=t["n"], user_code=t["c"], role="teacher",
                phone_number=generate_phone(),
                avatar=t["avt"],
                email=t["email"]
            )
            session.add(gv)
    session.commit()
    
    gv1 = session.query(User).filter_by(username="admin").first()
    gv2 = session.query(User).filter_by(username="gv002").first()

    # 2. Courses
    print("Creating Courses...")
    courses_data = [
        {"code": "7080518", "name": "Thị giác máy tính", "teacher": gv1, "credits": 3},
        {"code": "7080122", "name": "Trí tuệ nhân tạo", "teacher": gv1, "credits": 4},
        {"code": "7080116", "name": "Lập trình Web nâng cao", "teacher": gv2, "credits": 3},
        {"code": "7080514", "name": "Internet vạn vật (IoT)", "teacher": gv2, "credits": 2},
    ]
    
    course_objects = []
    for c_data in courses_data:
        existing = session.query(Course).filter_by(course_code=c_data["code"]).first()
        if not existing:
            course = Course(course_code=c_data["code"], course_name=c_data["name"], teacher_id=c_data["teacher"].id)
            session.add(course)
            session.commit()
            course_objects.append(course)
            credits=c_data["credits"]
        else:
            course_objects.append(existing)

    # 3. Students
    print("Creating Students...")
    counter = 1 
    total_new = 0
    count_with_avatar = 0
    
    for course in course_objects:
        num_students = random.randint(15, 20)
        print(f" -> Course {course.course_name}: adding {num_students} students.")
        
        for _ in range(num_students):
            mssv = f"990000{counter:04d}"
            
            if session.query(User).filter_by(username=mssv).first():
                counter += 1
                continue

            name = generate_random_name()
            
            student_avatar_path = check_student_avatar(mssv)
            if student_avatar_path:
                count_with_avatar += 1
            email_sv = f"{mssv}@humg.edu.vn"
            user_sv = User(
                username=mssv, password="123", fullname=name, user_code=mssv, role="student"
            )
            session.add(user_sv)
            session.commit() 
            
            student = Student(
                mssv=mssv, name=name, dob=get_random_dob_2004(),          
                class_name=random.choice(CLASSES_ADMIN), 
                course_id=course.id,
                user_id=user_sv.id,
                avatar=student_avatar_path,
                email=email_sv
            )
            session.add(student)
            
            counter += 1
            total_new += 1

    session.commit()
    session.close()
    
    print("-" * 50)
    print(f"Done. Added {total_new} students.")
    print(f"{count_with_avatar} students have a photo in 'data/raw_faces'.")
    print("-" * 50)

if __name__ == "__main__":
    seed()