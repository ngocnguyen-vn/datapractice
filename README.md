# Dự án E_Data – Phân tích dữ liệu & Machine Learning – DATATHON 2026 Vòng 1

## Giới thiệu

Dự án phân tích bộ dữ liệu mô phỏng hoạt động của một doanh nghiệp thời trang thương mại điện tử tại Việt Nam (2012–2022). Mục tiêu là đánh giá hiệu quả các chương trình khuyến mãi, tìm ra nguyên nhân gây lỗ, đề xuất giải pháp tối ưu, đồng thời xây dựng mô hình dự báo doanh thu và giá vốn hàng bán cho giai đoạn 2023–2024.

Thông qua phân tích dữ liệu và machine learning, dự án cung cấp các insight chiến lược giúp doanh nghiệp ra quyết định dựa trên dữ liệu.

---

##  Bài toán
-  **Phần 1:** Đáp án 10 câu hỏi trắc nghiệm

- **Phần 2:** Phân tích hiệu quả khuyến mãi – Xác định chương trình khuyến mãi đang gây lỗ, nguyên nhân và đề xuất điều chỉnh.
- **Phần 3:** Dự báo doanh thu (Revenue) và giá vốn hàng bán (COGS) theo ngày cho 548 ngày tiếp theo (01/2023 – 07/2024).
- Đánh giá mô hình dự báo bằng các chỉ số MAE, RMSE, R².

---

##  Cấu trúc dự án

- `EDA_analysis.ipynb`: Phân tích hiệu quả khuyến mãi (Descriptive, Diagnostic, Predictive, Prescriptive)
- `part1_MCQ.ipynb`: Đáp án 10 câu hỏi trắc nghiệm
- `part3_ML.ipynb`: Xây dựng và đánh giá mô hình LightGBM cho dự báo doanh thu và COGS
- `EDA_dashboard.py`: Ứng dụng Streamlit dashboard trực quan hóa các insight chính
- `submission.csv`: Kết quả dự báo cho Kaggle
- `requirements.txt`: Danh sách thư viện cần cài đặt
- `README.md`: Tổng quan dự án

---

##  Phương pháp thực hiện

1. **Thu thập và làm sạch dữ liệu** – Đọc 14 bảng CSV, xử lý null, tạo các biến phụ (profit, margin, price_ratio).
2. **Phân tích khám phá (EDA)** – So sánh promo/non‑promo, xác định top promo lỗ nhất, phân tích chiến dịch Urban Blowout.
3. **Trực quan hóa dữ liệu** – Biểu đồ cột, thanh ngang, dumbbell chart, đường xu hướng tích lũy.
4. **Xây dựng mô hình Machine Learning** – LightGBM với 33 features (date, lag, traffic, inventory, promo).
5. **Đánh giá và rút ra insight** – Validation trên 2021–2022, phân tích feature importance.

---

## Kết quả chính

- **38,7%** đơn hàng có khuyến mãi nhưng lợi nhuận âm **-12,8%** (lỗ 678 triệu VND), trong khi đơn không khuyến mãi lãi **+20,8%** (2,2 tỷ VND).
- **5 chương trình khuyến mãi lỗ nhất** đều thuộc chiến dịch **Urban Blowout** (giảm 50% giá gốc).
- **Nguyên nhân lỗ cấu trúc:** 100% sản phẩm Urban có margin gốc < 50%, bán bằng 50% giá gốc là không thể có lãi.
- **Khách hàng Urban** có số đơn trung bình cao hơn **84,7%** và **92,6%** mua cả hàng không khuyến mãi → không nên cắt bỏ chiến dịch.
- **Đề xuất:** Tăng giá từ 50% lên 90% giá gốc → cải thiện lợi nhuận **+627 triệu VND** (từ lỗ 492 triệu thành lãi 135 triệu VND).
- **Mô hình dự báo:** LightGBM đạt **MAE = 629.087 VND**, **RMSE = 891.914 VND**, **R² = 0,714** trên tập validation 2021–2022.
- **Top features quan trọng:** `rev_lag_365`, `rev_monthly_avg`, `day`, `avg_sell_through`, `dayofweek`.

---

##  Công cụ sử dụng

- Python
- Pandas, NumPy
- Matplotlib, Seaborn, Plotly
- Scikit-learn, LightGBM
- Streamlit (dashboard)

---

## Kết luận

Dự án đã xác định thành công chiến dịch Urban Blowout lỗ là do chính sách giảm giá 50% trên sản phẩm có biên lợi nhuận thấp. Giải pháp tăng giá lên 90% giúp chuyển lỗ thành lãi mà vẫn giữ chân khách hàng trung thành. Mô hình LightGBM cung cấp dự báo doanh thu đáng tin cậy (R²=0.714), hỗ trợ lập kế hoạch kinh doanh. Quy trình phân tích từ mô tả, chẩn đoán, dự báo đến đề xuất hành động đã chứng minh giá trị của data‑driven decision making.
