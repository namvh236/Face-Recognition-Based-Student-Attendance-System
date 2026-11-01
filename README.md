# Face Recognition Based Student Attendance System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Framework](https://img.shields.io/badge/Framework-PyQt5-green?style=for-the-badge&logo=qt)
![AI Model](https://img.shields.io/badge/Model-RetinaFace%20%26%20ArcFace-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge)

**Hệ thống điểm danh sinh viên thông minh sử dụng Deep Learning với độ chính xác cao.**

</div>

---

## 📖 Giới Thiệu (Overview)

Dự án này là giải pháp chuyển đổi số cho việc quản lý lớp học, thay thế phương pháp điểm danh truyền thống. Hệ thống tích hợp các mô hình Deep Learning SOTA (**RetinaFace** cho phát hiện và **ArcFace** cho nhận diện) để đảm bảo khả năng nhận diện chính xác trong nhiều điều kiện môi trường khác nhau.

Giao diện người dùng được xây dựng bằng **PyQt5 (Widgets + QSS)**, trực quan và dễ thao tác cho giảng viên.

## 🚀 Tính Năng Nổi Bật (Key Features)

* **⚡ Real-time Inference:** Nhận diện và xử lý luồng video thời gian thực với độ trễ thấp (< 50ms/face).
* **🎯 Robust Accuracy:** Khả năng nhận diện tốt ngay cả khi khuôn mặt bị nghiêng, che khuất một phần, đeo kính hoặc thay đổi biểu cảm.
* **🖥 Modern UI/UX:** Giao diện PyQt5 trực quan cho giảng viên và sinh viên.
* **📊 Auto Logging:** Tự động ghi nhận thời gian ra/vào và xuất báo cáo điểm danh ra file Excel (.xlsx) hoặc CSV.
* **🛡 Anti-Spoofing (Basic):** Cơ chế lọc ngưỡng (thresholding) để giảm thiểu nhận diện sai.

## 🛠 Tech Stack

| Thành phần | Công nghệ / Thư viện | Chi tiết |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Ngôn ngữ lập trình chính |
| **GUI Framework** | PyQt5 (Widgets + QSS) | Giao diện người dùng |
| **Computer Vision** | OpenCV, Pillow | Xử lý ảnh đầu vào |
| **Face Detection** | RetinaFace | Mô hình phát hiện khuôn mặt (InsightFace) |
| **Face Recognition** | ArcFace (ResNet) | Trích xuất đặc trưng khuôn mặt (InsightFace) |
| **Data Processing** | Pandas, NumPy | Xử lý dữ liệu và xuất báo cáo |
| **Optimization** | ONNX Runtime | Tăng tốc độ inference trên CPU/GPU |

## 📂 Cấu Trúc Dự Án (Project Structure)

```bash
Face-Recognition-Based-Student-Attendance-System/
├── app/                        # Source code chính
│   ├── ui/                     # Giao diện PyQt5 (login, teacher, student, camera dialog)
│   ├── controllers/            # Logic nghiệp vụ, kết nối UI với database
│   ├── services/               # Nhận diện khuôn mặt (InsightFace, cache, cosine)
│   ├── database/               # SQLAlchemy engine + models
│   ├── config.py               # Đường dẫn và tham số cấu hình (nguồn duy nhất)
│   └── constants.py            # Hằng số trạng thái điểm danh
├── assets/                     # Tài nguyên tĩnh (icons, ảnh, file .qss)
├── data/                       # Dữ liệu runtime (tự sinh, KHÔNG commit)
│   ├── raw_faces/              # Ảnh gốc <MSSV>.jpg để dựng cache bằng script
│   ├── enrolled_faces/         # Ảnh chụp khi thêm sinh viên trong app
│   ├── face_data.pkl           # Embeddings { mssv: vector }
│   └── student_management.db   # SQLite
├── samples/                    # File Excel mẫu để import lớp học
├── scripts/                    # Script tiện ích (seed_data, build_face_cache)
├── docs/images/                # Ảnh minh hoạ cho README
├── main.py                     # Entry point của ứng dụng
├── requirements.txt            # Danh sách thư viện
└── README.md                   # Tài liệu dự án
```

## 🧠 Nguyên Lý Hoạt Động (Workflow)

Hệ thống hoạt động dựa trên luồng xử lý dữ liệu (pipeline) gồm 4 giai đoạn chính, kết hợp giữa mô hình phát hiện (Detection) và nhận diện (Recognition):

<img src="docs/images/pipeline_flow.png" alt="Attendance Success" width="50%">

1.  **Face Detection:** Quét toàn bộ khung hình để tìm vị trí khuôn mặt.
2.  **Face Alignment:** Căn chỉnh khuôn mặt dựa trên 5 điểm mốc (mắt, mũi, miệng) để chuẩn hóa góc nhìn.
3.  **Feature Extraction:** Chuyển đổi khuôn mặt thành vector 512 chiều.
4.  **Matching:** So sánh vector hiện tại với cơ sở dữ liệu vector đã đăng ký sử dụng độ đo Cosine Similarity.

## ⚙️ Cài Đặt (Installation)

### 1\. Yêu cầu (Prerequisites)

  * Python 3.10+ (đã kiểm tra trên 3.12)
  * Webcam (hoặc IP Camera)
  * **(Khuyến nghị)** NVIDIA GPU + CUDA để đạt FPS cao nhất.

### 2\. Các bước cài đặt

**Bước 1: Clone Repository**

```bash
git clone [https://github.com/devk1ngz/Face-Recognition-Based-Student-Attendance-System.git](https://github.com/devk1ngz/Face-Recognition-Based-Student-Attendance-System.git)
cd Face-Recognition-Based-Student-Attendance-System
```

**Bước 2: Thiết lập môi trường ảo**

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

**Bước 3: Cài đặt thư viện**

```bash
pip install -r requirements.txt
```

> *Lưu ý: Lần đầu chạy, thư viện `insightface` sẽ tự tải model (\~300MB), quá trình này có thể mất vài phút.*

## 📖 Hướng Dẫn Sử Dụng (User Guide)

1.  **Khởi chạy:**

    ```bash
    python main.py
    ```

2.  **Chuẩn bị dữ liệu (tuỳ chọn):**

    ```bash
    python -m scripts.seed_data          # tạo giảng viên/lớp/sinh viên mẫu (tài khoản admin / gv002, mật khẩu 123)
    python -m scripts.build_face_cache   # dựng data/face_data.pkl từ ảnh <MSSV>.jpg trong data/raw_faces/
    ```

3.  **Đăng ký sinh viên mới:**

      * Vào Tab **"Thêm sinh viên"**.
      * Nhập MSSV, Họ Tên, Ngày tháng năm sinh và tên lớp.
      * Nhấn **"Chụp ảnh"**: hệ thống lưu sinh viên vào database, lưu ảnh vào `data/enrolled_faces/` và cập nhật vector đặc trưng ngay lập tức (không cần bước huấn luyện riêng).

4.  **Điểm danh:**

      * Quay lại màn hình **Dashboard**.
      * Hệ thống tự động nhận diện và hiển thị thông tin lên màn hình.
      * Kết quả được lưu tự động vào hệ thống.

## 📸 Demo Hình Ảnh (Screenshots)

| Giao diện giáo viên | Giao diện sinh viên |
| :---: | :---: |
| ![Teacher Window](docs/images/teacher_ui.png) | ![Student Window](docs/images/student_ui.png) |
## Kết quả điểm danh ghi nhận

| Kết quả khi giáo viên điểm danh thành công|
| :---: |
| ![Attendance Success](docs/images/attendance_result.png) |



## 🤝 Đóng Góp (Contributing)

Mọi đóng góp (Pull Requests, Issues) đều được hoan nghênh\!
Nếu bạn thấy dự án hữu ích, hãy để lại một ⭐ **Star** nhé\!

## 📄 License

Dự án thuộc bản quyền **MIT License**.

-----

**Author:** [Devk1ngz](https://github.com/devk1ngz)
