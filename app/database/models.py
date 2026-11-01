from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.database.connector import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    fullname = Column(String)
    user_code = Column(String)
    email = Column(String)
    role = Column(String)
    phone_number = Column(String, nullable=True)
    courses = relationship("Course", back_populates="teacher")


class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    course_code = Column(String, unique=True)
    course_name = Column(String)
    credits = Column(Integer, default=3)
    teacher_id = Column(Integer, ForeignKey('users.id'))
    teacher = relationship("User", back_populates="courses")
    students = relationship("Student", back_populates="course")


class Student(Base):
    """One row per student. `mssv` is globally unique, so a student belongs to exactly one course."""
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    mssv = Column(String, unique=True)
    name = Column(String)
    dob = Column(Date, nullable=True)
    class_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    course = relationship("Course", back_populates="students")
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Login account, linked by MSSV on first sign-in


class Attendance(Base):
    __tablename__ = 'attendances'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    date = Column(String)
    time = Column(String)
    status = Column(String)
    note = Column(String, nullable=True)
