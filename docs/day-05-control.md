# Kiểm soát thực hiện Ngày 5 - Data Pipeline

## 1. Trạng thái

**Hoàn thành:** toàn bộ output bắt buộc trong kế hoạch Ngày 5 đã được triển khai và kiểm tra trên sample CICIDS2017 50.000 dòng.

| Output theo kế hoạch | Trạng thái | Ghi chú |
|---|---|---|
| `pipelines/ingest.py` | Hoàn thành | Đọc CSV, chuẩn hóa header, kiểm tra schema, thay Infinity, hỗ trợ CLI |
| `pipelines/preprocess.py` | Hoàn thành | Clean, encode, feature engineering, scale, xuất CSV + metadata |
| `data/processed/traffic_processed.csv` | Hoàn thành local | 45.857 dòng, 25 cột; được Git ignore đúng chính sách dữ liệu |
| `docs/features.md` | Hoàn thành | Mô tả source mapping, cleaning, feature, scaling, model contract và limitation |

Output bổ sung để tăng khả năng kiểm soát/chất lượng:

- `data/processed/preprocessing_metadata.json` (local): tham số impute/scale, model feature list, phân phối nhãn và thống kê cleaning.
- `tests/test_data_pipeline.py`: kiểm thử ingest, duplicate removal, Infinity, feature port, label mapping và ghi output.
- `pipelines/requirements.txt`: dependency tối thiểu có version range.
- `pipelines/__init__.py`: cho phép import pipeline như Python package.

## 2. Công việc đã thực hiện

### Ingestion

- Kiểm tra file input tồn tại, đúng định dạng CSV và có dữ liệu.
- Chuẩn hóa BOM/khoảng trắng/header về `snake_case`.
- Phát hiện tên cột bị trùng sau chuẩn hóa.
- Kiểm tra 7 cột bắt buộc của CICIDS2017 MVP.
- Thay `+inf/-inf` ở cột số bằng missing value và ghi lại số lượng.
- Hỗ trợ `--input`, `--output`, `--max-rows`.

### Cleaning và validation

- Loại 2.945 dòng duplicate chính xác ở raw data.
- Sau feature projection, loại thêm 1.198 dòng trùng `model features + target` để giảm train/test leakage.
- Giữ 32 feature vector có target xung đột để không che giấu nhiễu/ambiguity của nhãn.
- Coerce kiểu số; kiểm tra port `0..65535` và các đại lượng duration/packet/byte không âm.
- Loại record không có label (run hiện tại: 0 dòng).
- Median-impute các giá trị không hợp lệ/missing.
- Không cho NaN hoặc Infinity đi vào final dataset.
- Chuẩn hóa nhãn lỗi encoding dạng `Web Attack - ...`.

### Feature engineering và encoding

- Tạo `total_packets`, `total_bytes`, `bytes_per_packet`, `packets_per_second`, `bytes_per_second`.
- Giữ `dst_port`, `flow_duration_us`, các tổng/rate và `attack_type` ở đơn vị dễ đọc cho dashboard.
- Tạo cờ well-known/web/DNS/high port.
- One-hot encode 3 nhóm port: well-known, registered, dynamic/private.
- Map `BENIGN/NORMAL/0 -> 0`; nhãn khác `-> 1`.

### Scaling và reproducibility

- Áp dụng `log1p` để giảm skew, sau đó robust-scale bằng median/IQR cho 7 numeric model features.
- Ghi đầy đủ center/scale vào metadata JSON.
- Công bố danh sách 14 model features và target để Ngày 7 dùng trực tiếp.

## 3. Kết quả chạy dữ liệu thật

| Chỉ số | Kết quả |
|---|---:|
| Input | 50.000 dòng x 79 cột |
| Duplicate phát hiện/đã loại | 2.945 |
| Feature-level duplicate đã loại | 1.198 |
| Feature vector có target xung đột đã giữ | 32 |
| Output | 45.857 dòng x 25 cột |
| Normal (`binary_label = 0`) | 23.760 |
| Anomaly (`binary_label = 1`) | 22.097 |
| Missing cell ở output | 0 |
| Infinity ở numeric output | 0 |
| Duplicate nguyên dòng ở output | 0 |
| Kích thước processed CSV | khoảng 10,39 MiB |

Lưu ý kiểm soát: ingestion report ghi 64 Infinity được thay thành missing và tổng missing sau bước đó là 100. Trong các cột bắt buộc/derived, pipeline đã impute toàn bộ trước khi xuất.

## 4. Kiểm thử đã chạy

Lệnh:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Kết quả: **3/3 test PASS**.

| Test | Mục tiêu | Kết quả |
|---|---|---|
| `test_normalize_column_name` | Header có khoảng trắng và suffix `.1` được chuẩn hóa ổn định | PASS |
| `test_load_and_preprocess` | Infinity, duplicate, label, port flags, numeric finite | PASS |
| `test_write_outputs` | CSV và metadata JSON được ghi, target contract đúng | PASS |

Kiểm tra bổ sung trên full output:

- Shape đúng `45.857 x 25`.
- Không missing, không Infinity, không duplicate nguyên dòng.
- Các cột numeric đọc lại đúng kiểu số; `port_category` và `attack_type` là text.
- Metadata chứa đủ cleaning stats, distribution, output columns, model features và scaling parameters.

## 5. Cách chạy lại

Từ thư mục gốc repo:

```powershell
python -m pip install -r pipelines/requirements.txt
python pipelines/ingest.py
python pipelines/preprocess.py
python -m unittest discover -s tests -p "test_*.py" -v
```

Nếu chỉ muốn smoke test nhanh:

```powershell
python pipelines/preprocess.py --max-rows 100 --output data/processed/traffic_processed_smoke.csv --metadata-output data/processed/preprocessing_metadata_smoke.json
```

## 6. Definition of Done

- [x] Có `ingest.py` đọc/validate raw CSV.
- [x] Có `preprocess.py` clean, encode, scale và feature engineering.
- [x] Input/output path rõ, có default và CLI override.
- [x] Tạo được `traffic_processed.csv` từ sample thật.
- [x] Có `docs/features.md` giải thích feature network traffic.
- [x] Có metadata để tái sử dụng preprocessing.
- [x] Có automated tests và full-data validation.
- [x] Generated data không bị commit nhờ `.gitignore`.

## 7. Handoff sang Ngày 7

Ngày 7 nên đọc `model_feature_columns` và `target_column` trong `preprocessing_metadata.json`, sau đó:

1. Split dữ liệu có `stratify=binary_label` và random seed cố định.
2. Train baseline `RandomForestClassifier` (ưu tiên) và một model đơn giản để đối chiếu nếu thời gian cho phép.
3. Không scale lại các cột `feature_*_scaled`.
4. Báo cáo accuracy, precision, recall, F1 và confusion matrix; ưu tiên giải thích recall của anomaly.
5. Lưu cả model artifact và feature contract/metadata cùng version.

## 8. Giới hạn đã biết

- Sample hiện không có timestamp, IP và protocol; không được suy diễn/giả lập các feature này trong model.
- `record_id` chỉ có ý nghĩa trong artifact hiện tại, không dùng làm model feature.
- Class balance thay đổi nhẹ sau deduplicate; Ngày 7 phải stratify split.
- Processed CSV và metadata là artifact local bị Git ignore; khi clone máy khác phải chạy lại pipeline.
