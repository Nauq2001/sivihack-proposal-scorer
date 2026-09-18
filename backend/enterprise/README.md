# Kho tri thức doanh nghiệp (RAG)

Phần này **không** tham gia chấm điểm RFP/proposal. Việc chấm vẫn đọc nguyên văn
cả hai tài liệu, vì phải chứng minh được "proposal không hề nhắc tới X" — điều mà
truy xuất top-k không làm được. Kho này chỉ trả lời câu hỏi khác: *công ty mình
thường viết mục này thế nào, và bản nháp đang hứa gì vượt quá khả năng thật*.

Lỗi ở kho không được làm chết phần chấm chính: `main.py` nạp router trong
`try/except`.

## Dữ liệu

`backend/data/enterprise_demo/` — sao chép từ `proposal_scorer_benchmark/enterprise_demo`.
Toàn bộ **hư cấu**: 6 proposal đã ẩn danh, 1 rate card, 1 chuẩn SLA, 3 điều khoản
mẫu, 1 lịch sử review, 34 chunk cắt theo heading và vai trò mục.

## Cổng nạp

`store.py` **tự chạy lại cổng kiểm soát** thay vì tin vào cờ `demo_gate_result`
có sẵn trong file, vì một cờ tự khai không chứng minh được nội dung đã sạch.

| Luật | Hệ quả |
|---|---|
| Thiếu một trong các trường bắt buộc (ngành, quốc gia, loại dịch vụ, khoảng giá trị, kết quả, điểm, ngày gửi) | Từ chối |
| `status = draft` | Từ chối |
| Điểm chất lượng không do API chấm lúc nạp | Demo: cảnh báo. **Production: từ chối** |
| Tài liệu hư cấu | Production: từ chối |
| Chưa ẩn danh tên khách hoặc số tiền | Không được dùng giữa các deal |
| Rate card / SLA quá 6 tháng | Vẫn đọc được, nhưng **không được khẳng định là chuẩn hiện hành**; mọi phát hiện dựa vào nó hạ xuống mức `check` |

Chunk của tài liệu bị từ chối cũng bị loại khỏi index.

Chạy `load_corpus(production=True)` với bộ fixture hiện tại sẽ nạp **0 tài liệu**,
đúng như mong đợi: điểm trong fixture là `mock_scoring_api`. Khi nối API chấm thật
lúc nạp thì chuyển sang chế độ production.

## Bốn ô thắng/thua × viết tốt/kém

`Record.role` tự tính, không lấy từ file:

| Kết quả | Điểm ≥ 4 | Điểm < 3 |
|---|---|---|
| **Thắng** | `gold_reference` — được dùng làm mẫu để noi theo | `context_only` — thắng vì lý do khác, **không** làm mẫu |
| **Thua** | `context_only` — không thua vì cách viết | `anti_pattern` — dùng làm cảnh báo |

Điểm 3 đến dưới 4 là `intermediate`, không ép thành tốt hay kém.

Với bộ hiện tại: gold = proposal_01, 02, 03 · anti-pattern = proposal_06 ·
context_only = proposal_04 (thắng nhưng viết kém), proposal_05 (thua nhưng viết tốt).

## Truy xuất hoạt động thế nào

**Lọc metadata trước, xếp hạng văn bản sau.** Lọc trước là thứ ngăn công cụ trích
một deal đã thua như thể đó là mẫu tốt.

Xếp hạng dùng BM25 viết tay trong `retrieve.py`, không có vector DB, không gọi
embedding. Với vài chục chunk thì nó đủ, chạy offline, và **cho cùng một kết quả
mỗi lần** — điều này quan trọng khi người duyệt muốn kiểm chứng lại. Khi kho lên
tới hàng nghìn chunk thì thêm embedding, chữ ký hàm không cần đổi.

## API

```bash
# Kho đang nhận những gì, từ chối gì và vì sao
curl localhost:8000/api/evidence/corpus

# Mục giá của các proposal vừa thắng vừa viết tốt
curl -X POST localhost:8000/api/evidence/benchmark \
  -H 'Content-Type: application/json' \
  -d '{"section_role":"pricing","country":"DE"}'

# Bản nháp đang hứa gì vượt quá khả năng công ty
curl -X POST localhost:8000/api/evidence/commitments \
  -H 'Content-Type: application/json' \
  -d '{"text":"We offer 24/7 support and resolve incidents within 4 hours at €400 per day."}'

# Tìm tự do
curl -X POST localhost:8000/api/evidence/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"phased rollout pilot","limit":3}'

# Toàn văn bản đã ẩn danh
curl localhost:8000/api/evidence/document/proposal_01
```

`section_role` hiện có: `solution` (22 chunk), `pricing` (5), `support_sla` (3),
`risks` (3), `timeline` (1).

## Kiểm tra lời hứa

`evidence.py` — **không dùng model, không truy xuất**, chỉ khớp chuỗi, nên chạy lại
bao nhiêu lần cũng ra một kết quả. Mỗi phát hiện kèm **câu trích nguyên văn** từ
bản nháp và trỏ tới đúng trường trong tài liệu chuẩn.

| Luật | Bắt cái gì |
|---|---|
| `coverage_beyond_capability` | Hứa 24/7 trong khi `24_7_on_call_available = false` |
| `coverage_outside_standard_hours` | Hứa hỗ trợ cuối tuần hoặc ngày lễ, ngoài giờ chuẩn |
| `restoration_guarantee` | Hứa **khắc phục xong** trong X giờ; chuẩn công ty chỉ cam kết thời gian phản hồi |
| `day_rate_below_floor` | Đơn giá ngày thấp hơn sàn trong rate card |

Thêm luật mới: viết regex, gọi `_finding(...)` với `record_id` và tên trường của
tài liệu chuẩn, rồi bổ sung một ca vào `selftest.py`.

## Tự kiểm tra

```bash
cd backend && python3 -m enterprise.selftest
```

Không cần mạng, không cần API key. Nó in báo cáo cổng nạp, chạy các truy vấn demo,
kiểm tra chế độ production từ chối đúng, và xác nhận **mọi câu trích có mặt nguyên
văn** trong bản nháp.

## Giới hạn đã biết của bộ dữ liệu

- Chỉ có **1 chunk `timeline`** trên cả 6 proposal, nên chưa so sánh mục tiến độ được.
- Lọc mục giá (won, điểm ≥ 4, DE) trả về **2 tài liệu**, không phải 3. Đừng nói
  "3/3" khi truy vấn thật chỉ trả về 2 — README của kho cũng dặn đúng điều này.
- Chunk đầu của mỗi proposal gắn `section_role` theo mục kế tiếp, nên dòng
  "Submitted by: [ENTITY]" đang nằm trong `support_sla`. Không ảnh hưởng kết quả
  lọc, nhưng nếu sửa lại nhãn thì sạch hơn.
- Ba mẫu vàng thuộc **ba ngành khác nhau**, nên không dùng được để demo "so sánh
  ba bản cùng ngành". Muốn vậy phải thêm dữ liệu.
