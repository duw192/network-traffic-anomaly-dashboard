# Day 03 - Dataset and Problem Definition Guide

## Muc tieu

Ngay 3 chot dataset, bai toan phan loai, schema du lieu va notebook kham pha ban dau. Ket qua cua ngay nay phai du ro de ngay 5 co the viet `pipelines/ingest.py` va `pipelines/preprocess.py` ma khong phai doi lai huong du lieu.

Theo ke hoach 3 tuan, output bat buoc:

- `data/raw/sample.csv`
- `docs/dataset.md`
- `notebooks/01_data_exploration.ipynb`

Repo cung cap them script ho tro:

- `scripts/create_dataset_sample.py`

Trang thai Day 03 hien tai: dataset CICIDS2017 da duoc dat tai `data/raw/MachineLearningCVE/`, sample da duoc tao tai `data/raw/sample.csv`, notebook exploration da san sang. `pipelines/` va `ml/` van chua co implementation vi do la pham vi ngay 5 va ngay 7.

## Khuyen nghi dataset

Nen uu tien `CICIDS2017` cho MVP nay.

Ly do:

- Phu hop dung bai toan Network Traffic Anomaly Dashboard: du lieu flow-based, co CSV cho machine learning.
- Co label benign/attack, de quy ve binary label `0 = normal`, `1 = anomaly`.
- Co nhieu feature network flow nhu duration, packet, byte, destination port va label.
- De giai thich trong portfolio hon cac dataset qua phuc tap.

Phuong an du phong la `UNSW-NB15`, cung co label va training/testing CSV san, nhung feature schema khac nhieu hon so voi schema logical trong `docs/architecture.md`.

Nguon nen ghi vao `docs/dataset.md`:

- CICIDS2017: https://www.unb.ca/cic/datasets/ids-2017.html
- UNSW-NB15: https://research.unsw.edu.au/projects/unsw-nb15-dataset

## Pham vi ngay 3

Lam:

- Chon dataset chinh.
- Tai hoac lay mot file CSV dai dien.
- Tao sample nho 20k-50k dong de demo nhanh.
- Xac dinh cot label va mapping ve binary anomaly.
- Lap bang mapping tu cot goc sang schema logical cua do an.
- Kiem tra nhanh missing values, duplicate, class distribution, numeric ranges.
- Ghi lai quyet dinh trong `docs/dataset.md`.

Chua lam:

- Chua train model.
- Chua viet preprocessing day du.
- Chua lam backend/frontend.
- Chua dua raw dataset lon vao Git.

## Schema logical can chot

Do an dang ky vong cac field logic sau trong `docs/architecture.md`:

| Logical field | Bat buoc | Ghi chu |
|---|---:|---|
| `timestamp` | Khuyen nghi | Khong co trong sample `MachineLearningCVE` hien tai |
| `src_ip` | Khuyen nghi | Khong co trong sample `MachineLearningCVE` hien tai |
| `dst_ip` | Khuyen nghi | Khong co trong sample `MachineLearningCVE` hien tai |
| `src_port` | Khuyen nghi | Khong co trong sample `MachineLearningCVE` hien tai |
| `dst_port` | Co | Dung cho port category |
| `protocol` | Khuyen nghi | Khong co trong sample `MachineLearningCVE` hien tai |
| `duration` | Co | Dung tao rate features |
| `bytes` | Co | Tong bytes hoac tong forward/backward bytes |
| `packets` | Co | Tong packets hoac tong forward/backward packets |
| `label` | Bat buoc | Mapping thanh `0 = normal`, `1 = anomaly` |

Vi sample hien tai khong co `src_ip`, `dst_ip`, `timestamp` va `protocol`, MVP van lam duoc bang flow features. Dashboard nen doi top IP/protocol distribution thanh destination port distribution, attack label distribution, anomaly rate va byte/packet/rate metrics.

## Cach tao `data/raw/sample.csv`

Khong commit dataset lon. `.gitignore` hien da ignore `data/raw/*`, vi vay sample that co the nam local trong `data/raw/sample.csv`.

Quy trinh:

1. Tai dataset CSV ve may.
2. Chon mot file co ca normal va attack.
3. Lay sample co can bang tuong doi giua normal/anomaly.
4. Giu header goc, chua doi ten cot o buoc nay.
5. Luu vao `data/raw/sample.csv`.

Dung script co san de tao sample ma khong can load toan bo CSV lon vao RAM:

```powershell
python scripts/create_dataset_sample.py data/raw/MachineLearningCVE/<source-file>.csv --output data/raw/sample.csv
```

Neu muon lay mau tu nhieu CSV:

```powershell
python scripts/create_dataset_sample.py data/raw/MachineLearningCVE/<file-1>.csv data/raw/MachineLearningCVE/<file-2>.csv --output data/raw/sample.csv
```

## Noi dung notebook `01_data_exploration.ipynb`

Notebook chi can kham pha va dua ra quyet dinh, khong bien thanh pipeline san xuat.

Thu tu cell nen co:

1. Load `data/raw/sample.csv`.
2. In shape, columns, 5 dong dau.
3. Chuan hoa ten cot tam thoi de doc de hon.
4. Xac dinh cot label va in class distribution.
5. Kiem tra missing values va duplicate rows.
6. Kiem tra numeric columns: min, max, mean, percentile 95.
7. Kiem tra protocol/port neu co.
8. De xuat feature engineering cho ngay 5:
   - `bytes_per_packet`
   - `packets_per_second`
   - `bytes_per_second`
   - `port_category`
   - destination-port flags
9. Ghi ket luan: dataset dung duoc/khong, label mapping, cot can drop, risk.

## Definition of Done

Ngay 3 duoc xem la xong khi:

- `data/raw/sample.csv` ton tai local va co ca normal/anomaly.
- `docs/dataset.md` ghi ro dataset, source, schema, label mapping va cac cot se dung.
- `notebooks/01_data_exploration.ipynb` chay duoc tu dau den cuoi voi sample.
- Da biet ngay 5 can clean cot nao, encode cot nao, tao feature nao.
- Khong commit dataset lon, khong commit file tam hoac output notebook qua nang.

## Phan cong nhom 2 nguoi

Thanh vien Data/ML/Backend:

- Tai dataset, tao `sample.csv`.
- Kiem tra schema, missing values, label distribution.
- Viet notebook exploration.
- Cap nhat `docs/dataset.md` phan technical.

Thanh vien Network/Frontend support:

- Giai thich y nghia protocol, port, flow duration, bytes, packets.
- De xuat chart dashboard dua tren dataset thuc te.
- Viet phan network context va limitation trong `docs/dataset.md`.
