# Network Traffic Anomaly Dashboard - Project Plan

# Kế hoạch dự án Network Traffic Anomaly Dashboard

---

## 1. Project Overview

Network Traffic Anomaly Dashboard is a portfolio project that detects abnormal network traffic from flow-based CSV data and presents the result through a web dashboard.

The project is designed for a two-person team and focuses on building a complete MVP within three weeks. The final system should include data processing, machine learning baseline, backend APIs, frontend visualization, documentation, and deployment instructions.

### 🇻🇳 Tiếng Việt

Network Traffic Anomaly Dashboard là một dự án portfolio nhằm phát hiện các bất thường trong lưu lượng mạng từ dữ liệu CSV dạng flow và hiển thị kết quả thông qua một bảng điều khiển (dashboard) trên web.

Dự án được xây dựng cho nhóm gồm **2 thành viên**, với mục tiêu hoàn thành một **MVP (Minimum Viable Product)** trong **3 tuần**. Hệ thống cuối cùng sẽ bao gồm:

- Pipeline xử lý dữ liệu
- Mô hình Machine Learning cơ bản
- Backend API
- Dashboard trực quan
- Tài liệu dự án
- Hướng dẫn triển khai

---

## 2. Final Goal

By the end of the project, the repository should include:

- A data pipeline for reading and processing network traffic CSV files.
- A cleaned and feature-engineered processed dataset.
- A baseline anomaly detection model.
- Model evaluation reports and metrics.
- A FastAPI backend exposing traffic, alert, metric, and prediction APIs.
- A React dashboard showing network traffic insights.
- A database or mock database for demonstration.
- Docker Compose setup for running the project.
- Clear documentation suitable for a student portfolio.

### 🇻🇳 Tiếng Việt

Sau khi hoàn thành dự án, repository cần bao gồm:

- Pipeline đọc và xử lý dữ liệu CSV của lưu lượng mạng.
- Bộ dữ liệu đã được làm sạch và thực hiện Feature Engineering.
- Mô hình phát hiện bất thường (Baseline Model).
- Báo cáo đánh giá mô hình cùng các chỉ số (Metrics).
- Backend FastAPI cung cấp API cho:
  - Traffic
  - Alert
  - Metrics
  - Prediction
- Dashboard React trực quan hóa dữ liệu mạng.
- Database (PostgreSQL hoặc SQLite) hoặc Mock Database để demo.
- Docker Compose giúp chạy toàn bộ hệ thống.
- Tài liệu đầy đủ phục vụ portfolio và CV.

---

## 3. MVP Scope

The MVP focuses on making the system runnable and explainable. The first version does not need advanced detection techniques or a complex UI.

### In Scope

- CSV-based network traffic dataset.
- Binary classification: normal traffic vs anomaly traffic.
- Basic preprocessing and feature engineering.
- Baseline model using Random Forest, Logistic Regression, or Isolation Forest.
- REST APIs using FastAPI.
- Dashboard pages for overview, traffic logs, alerts, and model metrics.
- Documentation for dataset, architecture, API, modeling, and deployment.

### Out of Scope

- Real-time packet capture.
- Deep learning models.
- Complex user authentication.
- Production cloud deployment.
- Enterprise-level monitoring features.

### 🇻🇳 Tiếng Việt

MVP hướng đến việc tạo ra một hệ thống **hoạt động được**, **dễ giải thích**, và **đủ để trình bày trong portfolio**.

### Phạm vi thực hiện

- Dataset lưu lượng mạng ở dạng CSV.
- Phân loại nhị phân:
  - Bình thường (Normal)
  - Bất thường (Anomaly)
- Tiền xử lý dữ liệu.
- Feature Engineering.
- Mô hình Baseline:
  - Random Forest
  - Logistic Regression
  - Isolation Forest
- REST API bằng FastAPI.
- Dashboard gồm:
  - Tổng quan hệ thống
  - Nhật ký lưu lượng
  - Danh sách cảnh báo
  - Chỉ số mô hình
- Tài liệu:
  - Dataset
  - Kiến trúc
  - API
  - Machine Learning
  - Deployment

### Không nằm trong phạm vi

- Thu thập packet theo thời gian thực.
- Deep Learning.
- Hệ thống đăng nhập phức tạp.
- Triển khai Production trên Cloud.
- Các chức năng giám sát doanh nghiệp.

---

## 4. Tech Stack

| Layer | Technology | Purpose |
|-------|------------|----------|
| Data Processing | Python, Pandas, NumPy | Clean and transform raw CSV data |
| Machine Learning | scikit-learn, joblib | Train and save baseline anomaly detection model |
| Backend | FastAPI, Pydantic | Provide REST APIs |
| Database | PostgreSQL or SQLite | Store traffic logs and alerts |
| Frontend | React, TypeScript, Vite, Tailwind CSS | Build dashboard UI |
| Visualization | Recharts or Chart.js | Display charts and metrics |
| Deployment | Docker, Docker Compose | Run all services together |
| Documentation | Markdown | Explain architecture, dataset, API, and model |

### 🇻🇳 Tiếng Việt

| Thành phần | Công nghệ | Mục đích |
|------------|-----------|----------|
| Xử lý dữ liệu | Python, Pandas, NumPy | Làm sạch và biến đổi dữ liệu CSV |
| Machine Learning | scikit-learn, joblib | Huấn luyện và lưu mô hình phát hiện bất thường |
| Backend | FastAPI, Pydantic | Xây dựng REST API |
| Database | PostgreSQL / SQLite | Lưu traffic và cảnh báo |
| Frontend | React, TypeScript, Vite, Tailwind CSS | Xây dựng Dashboard |
| Visualization | Recharts / Chart.js | Hiển thị biểu đồ |
| Deployment | Docker, Docker Compose | Chạy toàn bộ hệ thống |
| Documentation | Markdown | Viết tài liệu dự án |

---

## 5. Timeline

### Week 1 – Data and ML Baseline

Main objective: prepare dataset, build preprocessing pipeline, and train the first baseline model.

### 🇻🇳 Tuần 1 – Dữ liệu và Machine Learning

**Mục tiêu**

- Chuẩn bị dataset.
- Xây dựng pipeline đọc dữ liệu.
- Làm sạch dữ liệu.
- Feature Engineering.
- Huấn luyện mô hình đầu tiên.
- Đánh giá kết quả.

**Sản phẩm cần hoàn thành**

- `data/raw/sample.csv`
- `docs/dataset.md`
- `pipelines/ingest.py`
- `pipelines/preprocess.py`
- `data/processed/traffic_processed.csv`
- `ml/train.py`
- `ml/evaluate.py`
- `models/baseline_model.pkl`
- `reports/model_metrics.json`

---

### Week 2 – Backend and Dashboard

Main objective: build APIs and create the first dashboard version.

### 🇻🇳 Tuần 2 – Backend và Dashboard

**Mục tiêu**

- Xây dựng Backend bằng FastAPI.
- Thiết kế API.
- Xây dựng Dashboard React.
- Kết nối dữ liệu giữa Backend và Frontend.

**Sản phẩm cần hoàn thành**

- `backend/app/main.py`
- `backend/app/api/routes.py`
- `backend/app/schemas.py`
- `backend/app/services/prediction_service.py`
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/pages/TrafficLogs.tsx`
- `frontend/src/pages/Alerts.tsx`
- `frontend/src/pages/ModelMetrics.tsx`

---

### Week 3 – Integration and Demo

Main objective: connect all components, polish documentation, and prepare final demo.

### 🇻🇳 Tuần 3 – Tích hợp và Demo

**Mục tiêu**

- Tích hợp toàn bộ hệ thống.
- Kiểm thử.
- Hoàn thiện Docker.
- Viết tài liệu.
- Chuẩn bị demo và video.

**Sản phẩm cần hoàn thành**

- `docker-compose.yml`
- `.env.example`
- `README.md`
- `docs/api.md`
- `docs/modeling.md`
- `docs/deployment.md`
- Dashboard screenshots
- Demo video script

---

## 6. Team Responsibilities

| Member | Main Role | Responsibilities |
|--------|-----------|------------------|
| Member 1 | Data / ML / Backend | Data ingestion, preprocessing, model training, FastAPI backend, technical documentation |
| Member 2 | Network / Frontend Support | Network feature explanation, alert severity design, dashboard metrics, UI charts, traffic analysis documentation |

### 🇻🇳 Tiếng Việt

| Thành viên | Vai trò | Công việc |
|------------|----------|-----------|
| Thành viên 1 | Data / ML / Backend | Thu thập dữ liệu, tiền xử lý, huấn luyện mô hình, xây dựng FastAPI, viết tài liệu kỹ thuật |
| Thành viên 2 | Network / Frontend | Phân tích đặc trưng mạng, thiết kế mức độ cảnh báo, xây dựng Dashboard, trực quan hóa dữ liệu, viết tài liệu phân tích lưu lượng |

---

## 7. Working Rules

- Do not commit directly to `main`.
- Each task must have a GitHub Issue.
- Each feature should be developed on a separate branch.
- Pull Requests should be used before merging into `main`.
- Commit messages should follow a clear format.

Recommended commit types:

```text
feat: add new feature
fix: fix bug
docs: update documentation
refactor: improve code structure
chore: setup or maintenance task
```

### 🇻🇳 Tiếng Việt

Quy tắc làm việc của nhóm:

- Không commit trực tiếp lên `main`.
- Mỗi công việc phải có một GitHub Issue.
- Mỗi tính năng được phát triển trên một branch riêng.
- Tạo Pull Request trước khi merge vào `main`.
- Commit tuân theo chuẩn **Conventional Commits**.

### Ý nghĩa các loại commit

| Commit | Ý nghĩa |
|---------|----------|
| `feat:` | Thêm tính năng mới |
| `fix:` | Sửa lỗi |
| `docs:` | Cập nhật tài liệu |
| `refactor:` | Cải thiện cấu trúc code, không thay đổi chức năng |
| `chore:` | Công việc bảo trì, cài đặt môi trường, nâng cấp thư viện hoặc cấu hình dự án |