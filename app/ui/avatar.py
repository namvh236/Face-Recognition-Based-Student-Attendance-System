"""Circular avatar rendering and photo lookup shared by the teacher and student windows."""
import os

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPixmap

from app.config import ENROLLED_FACES_DIR, IMG_DIR, RAW_FACES_DIR

PHOTO_EXTENSIONS = (".jpg", ".jpeg", ".png")


def _first_existing(directory, stems):
    for stem in stems:
        for ext in PHOTO_EXTENSIONS:
            path = os.path.join(directory, f"{stem}{ext}")
            if os.path.exists(path):
                return path
    return None


def find_student_photo(mssv):
    """Photo captured at enrollment, or a hand-placed one in data/raw_faces."""
    return _first_existing(ENROLLED_FACES_DIR, [mssv]) or _first_existing(RAW_FACES_DIR, [mssv])


def find_teacher_photo(code, fullname=""):
    return _first_existing(os.path.join(IMG_DIR, "teacher"), [code, code.lower(), fullname])


def circular_pixmap(size, image_path=None, fallback_text="", fallback_color="#bdc3c7",
                    ring_color="white", ring_width=3, font_size=None):
    """Round avatar: the photo if it loads, otherwise a colored disc with `fallback_text`."""
    photo = QPixmap(image_path) if image_path else None
    if photo is not None and photo.isNull():
        photo = None

    result = QPixmap(size, size)
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    clip = QPainterPath()
    clip.addEllipse(0, 0, size, size)
    painter.setClipPath(clip)

    if photo:
        painter.drawPixmap(0, 0, photo.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
    else:
        painter.setBrush(QColor(fallback_color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, size, size)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", font_size or size // 3, QFont.Bold))
        painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, fallback_text)

    painter.setClipping(False)
    pen = QPen(QColor(ring_color))
    pen.setWidth(ring_width)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    inset = ring_width // 2
    painter.drawEllipse(inset, inset, size - 2 * inset, size - 2 * inset)
    painter.end()
    return result
