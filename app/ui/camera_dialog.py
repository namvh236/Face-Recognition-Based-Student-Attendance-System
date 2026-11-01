import cv2
import numpy as np
import unicodedata
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from app.config import CAMERA_INDEX, SIMILARITY_THRESHOLD
from app.constants import STATUS_PRESENT
from app.controllers.teacher_controller import load_known_faces, update_attendance
from app.services.face_service import cosine_similarities, get_face_app


class RecognitionThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    update_status_signal = pyqtSignal(str, str)

    def __init__(self, course_id):
        super().__init__()
        self.course_id = course_id
        self.is_running = True
        self.known_embeddings = []
        self.known_mssvs = []
        self.known_names = []

    def remove_accents(self, input_str):
        if not input_str:
            return ""
        s = unicodedata.normalize('NFD', input_str)
        s = s.encode('ascii', 'ignore').decode('utf-8')
        return str(s)

    def run(self):
        face_app = get_face_app()
        print("Đang tải dữ liệu vector khuôn mặt...")
        self.known_embeddings, self.known_mssvs, self.known_names = load_known_faces(self.course_id)
        
        self.known_embeddings = np.array(self.known_embeddings)
        print(f"Đã tải {len(self.known_mssvs)} sinh viên.")

        cap = cv2.VideoCapture(CAMERA_INDEX)
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret: break
            
            faces = face_app.get(frame)

            for face in faces:
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
                
                name_display = "Unknown" 
                mssv_display = ""
                color = (0, 0, 255) 
                
                if len(self.known_embeddings) > 0:
                    sims = cosine_similarities(face.embedding, self.known_embeddings)
                    max_idx = np.argmax(sims)
                    max_sim = sims[max_idx]

                    if max_sim > SIMILARITY_THRESHOLD:
                        mssv_found = self.known_mssvs[max_idx] 
                        full_name = self.known_names[max_idx]
                        

                        name_display = self.remove_accents(full_name) 
                        mssv_display = f"MSSV: {mssv_found} ({int(max_sim*100)}%)" 
                        
                        color = (0, 255, 0) 
                        
                        self.update_status_signal.emit(str(mssv_found), full_name)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                

                cv2.putText(frame, name_display, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                if mssv_display:
                    cv2.putText(frame, mssv_display, (x1, y2 + 25), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            self.change_pixmap_signal.emit(frame)
        
        cap.release()

    def stop(self):
        self.is_running = False
        self.wait()

class CameraDialog(QDialog):
    def __init__(self, course_id, date_str, parent=None):
        super().__init__(parent)
        self.course_id = course_id
        self.date_str = date_str
        self.setWindowTitle(f"Điểm danh AI (InsightFace) - Ngày {date_str}")
        self.setFixedSize(1000, 700)
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.lbl_video = QLabel("Đang khởi động InsightFace...")
        self.lbl_video.setAlignment(Qt.AlignCenter)
        self.lbl_video.setStyleSheet("background-color: #2c3e50; color: white; font-size: 16px;")
        self.lbl_video.setFixedSize(960, 540)
        layout.addWidget(self.lbl_video)

        self.lbl_status = QLabel("Trạng thái: Đang chờ...")
        self.lbl_status.setStyleSheet("font-size: 18px; font-weight: bold; color: #34495e; margin-top: 10px;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)

        self.btn_close = QPushButton("KẾT THÚC")
        self.btn_close.setFixedHeight(50)
        self.btn_close.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; font-size: 16px;")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close)

        self.thread = RecognitionThread(self.course_id)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.update_status_signal.connect(self.handle_attendance)
        self.thread.start()

    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.lbl_video.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(960, 540, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def handle_attendance(self, student_id, name):
        self.lbl_status.setText(f"Đã nhận diện: {name}")
        self.lbl_status.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60; margin-top: 10px;")
        update_attendance(student_id, self.course_id, self.date_str, STATUS_PRESENT)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()