import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QTableWidget, QTableWidgetItem,
                             QHeaderView, QGraphicsDropShadowEffect, QLineEdit, QDialog, QAbstractItemView, QGridLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QPixmap
from app.config import IMG_DIR, STYLES_DIR
from app.constants import STATUS_ABSENT, STATUS_PRESENT
from app.controllers.student_controller import (
    get_student_by_user_id,
    get_student_attendance_history,
    get_student_course_details,
)
from app.ui.avatar import circular_pixmap, find_student_photo

AVATAR_COLORS = ["#1abc9c", "#2ecc71", "#3498db", "#9b59b6", "#34495e", "#f1c40f", "#e67e22", "#e74c3c", "#95a5a6"]


def student_avatar(student, size, ring_color, ring_width):
    """Round avatar from the student's photo, or a colored disc with their initial."""
    name = (student.name or "").strip()
    initial = name.split()[-1][0].upper() if name else "SV"
    color = AVATAR_COLORS[sum(map(ord, name)) % len(AVATAR_COLORS)]
    return circular_pixmap(size, find_student_photo(student.mssv), initial, color,
                           ring_color, ring_width, font_size=size // 3)


# Student profile dialog
class StudentProfileDialog(QDialog):
    def __init__(self, student_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hồ sơ sinh viên")
        self.setFixedSize(800, 750) 
        self.setStyleSheet("background-color: white; font-family: 'Segoe UI';")
        
        self.s_info = student_info
        self.course_data = get_student_course_details(student_info.id)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        self.setLayout(layout)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)

        self.ava = QLabel()
        self.ava.setFixedSize(140, 140) 
        self.ava.setAlignment(Qt.AlignCenter)
        self.load_avatar_circle() 

        lbl_name = QLabel(self.s_info.name.upper())
        lbl_name.setStyleSheet("font-size: 22px; font-weight: 900; color: #2c3e50; letter-spacing: 1px;")
        lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name.setWordWrap(True)
        
        lbl_mssv = QLabel(f"MSSV: {self.s_info.mssv}")
        lbl_mssv.setStyleSheet("font-size: 16px; color: #7f8c8d; font-weight: bold; background: #f1f2f6; padding: 5px 15px; border-radius: 15px;")
        lbl_mssv.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.ava, alignment=Qt.AlignCenter)
        header_layout.addWidget(lbl_name)
        header_layout.addWidget(lbl_mssv, alignment=Qt.AlignCenter)
        layout.addLayout(header_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #ecf0f1;")
        layout.addWidget(line)

        info_container = QFrame()
        info_container.setStyleSheet("background-color: white;")
        grid = QGridLayout()
        grid.setContentsMargins(20, 0, 20, 0)
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(15)

        style_lbl = "color: #95a5a6; font-size: 14px; font-weight: 600;"
        style_val = "color: #2c3e50; font-size: 16px; font-weight: bold;"

        dob_str = self.s_info.dob.strftime("%d/%m/%Y") if self.s_info.dob else "---"
        email_str = self.s_info.email or f"{self.s_info.mssv}@humg.edu.vn"

        grid.addWidget(QLabel("Ngày sinh:"), 0, 0)
        lbl_dob_val = QLabel(dob_str); lbl_dob_val.setStyleSheet(style_val)
        grid.addWidget(lbl_dob_val, 0, 1)

        grid.addWidget(QLabel("Email:"), 1, 0)
        lbl_email_val = QLabel(email_str); lbl_email_val.setStyleSheet(style_val)
        grid.addWidget(lbl_email_val, 1, 1)
        
        grid.addWidget(QLabel("Lớp:"), 2, 0)
        lbl_class_val = QLabel(self.s_info.class_name if self.s_info.class_name else "---"); lbl_class_val.setStyleSheet(style_val)
        grid.addWidget(lbl_class_val, 2, 1)

        for i in range(grid.rowCount()):
            item = grid.itemAtPosition(i, 0).widget()
            if item: item.setStyleSheet(style_lbl)

        info_container.setLayout(grid)
        layout.addWidget(info_container)

        layout.addSpacing(10)

        lbl_table_title = QLabel("LỚP HỌC PHẦN ĐANG THAM GIA")
        lbl_table_title.setStyleSheet("font-size: 14px; font-weight: 800; color: #34495e; text-transform: uppercase; border-left: 4px solid #3498db; padding-left: 10px;")
        layout.addWidget(lbl_table_title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["TÊN LỚP", "GIẢNG VIÊN", "SĐT"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #dfe6e9; border-radius: 8px; font-size: 14px; }
            QHeaderView::section { background-color: #f8f9fa; border: none; padding: 10px; font-weight: bold; color: #7f8c8d; text-transform: uppercase; font-size: 12px; }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #f1f2f6; }
            QTableWidget::item:selected { background-color: #e3f2fd; color: #2c3e50; }
        """)
        
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.Stretch)

        self.table.setRowCount(len(self.course_data))
        for r, data in enumerate(self.course_data):
            it_course = QTableWidgetItem(data['course_name'])
            it_course.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 0, it_course)
            it_teacher = QTableWidgetItem(data['teacher_name'])
            it_teacher.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 1, it_teacher)
            raw_phone = data['teacher_phone']
            fmt_phone = raw_phone
            if raw_phone and len(raw_phone) >= 10:
                fmt_phone = f"{raw_phone[:4]}.{raw_phone[4:7]}.{raw_phone[7:]}"
                
            it_phone = QTableWidgetItem(fmt_phone)
            it_phone.setTextAlignment(Qt.AlignCenter) 
            self.table.setItem(r, 2, it_phone)
            
        layout.addWidget(self.table)
        
        btn_close = QPushButton("Đóng hồ sơ")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton { background-color: #34495e; color: white; padding: 12px; border-radius: 8px; font-weight: bold; border: none; font-size: 14px; }
            QPushButton:hover { background-color: #2c3e50; }
        """)
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

    def load_avatar_circle(self):
        self.ava.setPixmap(student_avatar(self.s_info, size=140, ring_color="#3498db", ring_width=4))


# Status badge label
class StatusBadge(QLabel):
    def __init__(self, status):
        super().__init__(status)
        self.setAlignment(Qt.AlignCenter)
        bg = "#bdc3c7"
        if status == STATUS_PRESENT: bg = "#e8f5e9"; color="#27ae60"
        elif status == STATUS_ABSENT: bg = "#fff5f5"; color="#c62828"
        else: bg = "#f5f6fa"; color="#7f8c8d"
        
        self.setStyleSheet(f"""
            background-color: {bg}; color: {color}; 
            font-weight: bold; border-radius: 6px; 
            padding: 4px 8px; font-family: 'Segoe UI'; font-size: 13px;
        """)

# Main student window
class StudentWindow(QWidget):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self.student_info = None
        self.current_course_id = None
        self.course_buttons = [] 
        
        self.setWindowTitle("Cổng Thông Tin Sinh Viên")
        self.setMinimumSize(1280, 750)
        self.initUI()
        self.load_style()
        self.init_data()

    def load_style(self):
        path = os.path.join(STYLES_DIR, "student_style.qss")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f: self.setStyleSheet(f.read())

    def initUI(self):
        main_layout = QHBoxLayout(); main_layout.setContentsMargins(0,0,0,0); main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self.sidebar = QFrame(); self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(330)
        sidebar_layout = QVBoxLayout(); sidebar_layout.setContentsMargins(20,30,20,20); sidebar_layout.setSpacing(15)
        self.sidebar.setLayout(sidebar_layout)

        self.setup_profile(sidebar_layout)
        sidebar_layout.addSpacing(20)

        lbl_menu = QLabel("DANH SÁCH LỚP HỌC"); lbl_menu.setObjectName("sidebar_title")
        sidebar_layout.addWidget(lbl_menu)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Tìm lớp học...")
        self.txt_search.setObjectName("course_search")
        self.txt_search.textChanged.connect(self.filter_courses) 
        sidebar_layout.addWidget(self.txt_search)

        self.courses_box = QVBoxLayout(); self.courses_box.setSpacing(5)
        sidebar_layout.addLayout(self.courses_box)
        sidebar_layout.addStretch()

        self.btn_logout = QPushButton("Đăng xuất"); self.btn_logout.setObjectName("btn_logout")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        sidebar_layout.addWidget(self.btn_logout)

        content = QFrame(); content.setObjectName("content_area")
        content_layout = QVBoxLayout(); content_layout.setContentsMargins(40,40,40,30); content_layout.setSpacing(20)
        content.setLayout(content_layout)

        header_container = QFrame(); header_container.setObjectName("header_container")
        header_layout = QHBoxLayout(); header_layout.setContentsMargins(0,0,0,0)
        header_container.setLayout(header_layout)
        
        logo = QLabel(); logo.setFixedSize(70,70)
        lp = os.path.join(IMG_DIR, "logo_humg.jpg")
        if os.path.exists(lp): logo.setPixmap(QPixmap(lp).scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        title_info = QVBoxLayout(); title_info.setSpacing(2)
        lbl_school = QLabel("TRƯỜNG ĐẠI HỌC MỎ - ĐỊA CHẤT"); lbl_school.setObjectName("school_name")
        self.lbl_subj = QLabel("Chọn lớp để xem..."); self.lbl_subj.setObjectName("header_title")
        title_info.addWidget(lbl_school); title_info.addWidget(self.lbl_subj)
        
        header_layout.addWidget(logo); header_layout.addSpacing(15); header_layout.addLayout(title_info); header_layout.addStretch()

        stats_layout = QHBoxLayout(); stats_layout.setSpacing(15)
        self.stat_total = self.create_mini_stat("TỔNG SỐ", "0", "#34495e")
        self.stat_present = self.create_mini_stat("THAM GIA", "0", "#27ae60")
        self.stat_absent = self.create_mini_stat("VẮNG", "0", "#e74c3c")
        
        stats_layout.addWidget(self.stat_total); stats_layout.addWidget(self.stat_present); stats_layout.addWidget(self.stat_absent)
        header_layout.addLayout(stats_layout)
        content_layout.addWidget(header_container)

        action_bar = QHBoxLayout()
        lbl_table = QLabel("Lịch sử điểm danh chi tiết"); lbl_table.setStyleSheet("font-size: 18px; font-weight: 700; color: #2c3e50;")
        action_bar.addWidget(lbl_table)
        
        content_layout.addSpacing(10); content_layout.addLayout(action_bar)

        table_card = QFrame(); table_card.setObjectName("table_card")
        sh = QGraphicsDropShadowEffect(); sh.setBlurRadius(10); sh.setColor(QColor(0,0,0,10)); sh.setYOffset(2); table_card.setGraphicsEffect(sh)
        table_layout = QVBoxLayout(); table_layout.setContentsMargins(0,0,0,0); table_card.setLayout(table_layout)

        self.tb = QTableWidget(); self.tb.setColumnCount(6)
        self.tb.setHorizontalHeaderLabels(["NGÀY", "GIỜ", "GIẢNG VIÊN", "SĐT GV", "TRẠNG THÁI", "GHI CHÚ"])
        
        h = self.tb.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.Fixed); self.tb.setColumnWidth(0, 140)
        h.setSectionResizeMode(1, QHeaderView.Fixed); self.tb.setColumnWidth(1, 140)
        h.setSectionResizeMode(2, QHeaderView.Fixed); self.tb.setColumnWidth(2, 300)
        h.setSectionResizeMode(3, QHeaderView.Fixed); self.tb.setColumnWidth(3, 140)
        h.setSectionResizeMode(4, QHeaderView.Fixed); self.tb.setColumnWidth(4, 170)
        h.setSectionResizeMode(5, QHeaderView.Stretch)

        self.tb.verticalHeader().setVisible(False); self.tb.setSelectionBehavior(QTableWidget.SelectRows)
        self.tb.setEditTriggers(QTableWidget.NoEditTriggers); self.tb.setAlternatingRowColors(True); self.tb.setShowGrid(False)
        table_layout.addWidget(self.tb)

        content_layout.addWidget(table_card)
        main_layout.addWidget(self.sidebar); main_layout.addWidget(content)

    def setup_profile(self, layout):
        w = QWidget()
        l = QVBoxLayout(); l.setContentsMargins(0,0,0,0); l.setSpacing(10); w.setLayout(l)

        self.ava = QLabel(); self.ava.setFixedSize(100, 100); self.ava.setAlignment(Qt.AlignCenter); self.ava.setText("SV")
        self.ava.setStyleSheet("background-color: #ecf0f1; border-radius: 50px; color: #7f8c8d; font-weight: bold; font-size: 24px;")

        self.lname = QLabel("Loading..."); self.lname.setObjectName("profile_name"); self.lname.setAlignment(Qt.AlignCenter); self.lname.setWordWrap(True)
        self.lid = QLabel("..."); self.lid.setObjectName("profile_sub"); self.lid.setAlignment(Qt.AlignCenter)

        self.btn_profile_detail = QPushButton("Xem hồ sơ cá nhân")
        self.btn_profile_detail.setObjectName("btn_profile_detail_unique")
        self.btn_profile_detail.setCursor(Qt.PointingHandCursor)
        self.btn_profile_detail.setStyleSheet("""
            QPushButton#btn_profile_detail_unique { 
                background-color: transparent; 
                color: #3498db; 
                border: 1px solid #3498db; 
                border-radius: 15px; 
                padding: 5px 15px; 
                font-weight: bold; 
                font-size: 15px; 
            }
            QPushButton#btn_profile_detail_unique:hover { background-color: #3498db; color: white; }
        """)
        self.btn_profile_detail.clicked.connect(self.open_profile_dialog)

        l.addWidget(self.ava, alignment=Qt.AlignCenter)
        l.addWidget(self.lname)
        l.addWidget(self.lid)
        l.addWidget(self.btn_profile_detail, alignment=Qt.AlignCenter)
        layout.addWidget(w)

    def open_profile_dialog(self):
        if self.s_info:
            dialog = StudentProfileDialog(self.s_info, self)
            dialog.exec_()

    def create_mini_stat(self, label, value, color):
        frame = QFrame(); frame.setObjectName("mini_stat")
        frame.setStyleSheet(f"#mini_stat {{ background: white; border-radius: 8px; border-left: 4px solid {color}; border: 1px solid #eee; }}")
        frame.setFixedSize(120, 60)
        l = QVBoxLayout(); l.setContentsMargins(10,5,10,5); l.setSpacing(0)
        lbl = QLabel(label); lbl.setStyleSheet("color: #95a5a6; font-size: 11px; font-weight: bold;")
        val = QLabel(value); val.setObjectName("val"); val.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 800;")
        l.addWidget(lbl); l.addWidget(val)
        frame.setLayout(l)
        return frame

    def init_data(self):
        if not self.user_id: return
        self.s_info = get_student_by_user_id(self.user_id)
        if self.s_info:
            self.lname.setText(self.s_info.name)
            self.lid.setText(self.s_info.mssv)
            self.ava.setStyleSheet("background: transparent;")
            self.ava.setPixmap(student_avatar(self.s_info, size=100, ring_color="white", ring_width=3))
            
            self.load_courses()

    def load_courses(self):
        courses = get_student_course_details(self.s_info.id)
        for i in reversed(range(self.courses_box.count())): 
            self.courses_box.itemAt(i).widget().setParent(None)
        self.course_buttons.clear()

        for c in courses:
            b = QPushButton(c["course_name"])
            b.setCheckable(True); b.setObjectName("sidebar_btn")
            b.clicked.connect(lambda _, cid=c["course_id"], cn=c["course_name"]: self.sel_course(cid, cn))
            self.courses_box.addWidget(b); self.course_buttons.append(b) 
        if self.course_buttons: self.course_buttons[0].click()

    def filter_courses(self, text):
        text = text.lower().strip()
        for btn in self.course_buttons:
            if text in btn.text().lower(): btn.setVisible(True)
            else: btn.setVisible(False)

    def sel_course(self, cid, cn):
        self.current_course_id = cid; self.lbl_subj.setText(cn)
        for b in self.course_buttons: b.setChecked(False)
        self.sender().setChecked(True)
        self.refresh()

    def refresh(self):
        if not self.current_course_id: return
        hist = get_student_attendance_history(self.s_info.id, self.current_course_id)
        
        tot = len(hist); pre = sum(1 for x in hist if x['status'] == STATUS_PRESENT); ab = sum(1 for x in hist if x['status'] == STATUS_ABSENT)
        self.stat_total.findChild(QLabel, "val").setText(str(tot))
        self.stat_present.findChild(QLabel, "val").setText(str(pre))
        self.stat_absent.findChild(QLabel, "val").setText(str(ab))

        self.tb.setRowCount(tot)
        for r, i in enumerate(hist):
            self.tb.setRowHeight(r, 60)
            
            display_date = i['date']
            q_date = QDate.fromString(i['date'], "yyyy-MM-dd")
            if q_date.isValid(): display_date = q_date.toString("dd-MM-yyyy")
            da = QTableWidgetItem(display_date); da.setTextAlignment(Qt.AlignCenter); self.tb.setItem(r, 0, da)
            
            ti = QTableWidgetItem(i['time']); ti.setTextAlignment(Qt.AlignCenter); self.tb.setItem(r, 1, ti)
            
            t_name = i.get('teacher_name', '---')
            it_name = QTableWidgetItem(t_name); it_name.setTextAlignment(Qt.AlignCenter); self.tb.setItem(r, 2, it_name)
            
            t_phone = i.get('teacher_phone', '---')
            it_phone = QTableWidgetItem(t_phone); it_phone.setTextAlignment(Qt.AlignCenter); self.tb.setItem(r, 3, it_phone)
            
            self.tb.setCellWidget(r, 4, StatusBadge(i['status']))
            
            no = QTableWidgetItem(i['note']); no.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter); self.tb.setItem(r, 5, no)