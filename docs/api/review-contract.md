# Hợp đồng API — `POST /api/review`

Frontend chạy **một chiều**: nhập tài liệu → chạy → đọc kết quả. Không còn bước
người dùng chỉnh tiêu chí, nên **một lần gọi duy nhất** trả về tất cả: phân tích
RFP, danh sách tiêu chí đã chốt kèm trọng số, và kết quả chấm.

- Frontend gọi: `frontend/src/api/review.js`
- Dữ liệu mẫu (chính là response thật): `frontend/src/mocks/response_*.json`
- Hình dạng bám theo `agent/contracts/scoring-input.schema.json` của RFP Analyst
  và `proposal_scorer_benchmark/evaluation_output.schema.json` của phần chấm điểm.

---

## 1. Request

```json
{
  "rfp":      { "name": "rfp_nordframe.md", "text": "# Request for Proposal ..." },
  "proposal": { "name": "response_1_weak.md", "text": "# Proposal: ..." }
}
```

Chỉ hai tài liệu. Tiêu chí không gửi lên nữa: RFP Analyst tự đọc RFP ra tiêu chí
và trọng số, rồi chuyển thẳng sang Scoring Agent.

---

## 2. Response

Ba khối: `rfp_analysis`, `confirmed_criteria`, `evaluation`.

### 2.1 `rfp_analysis`

| Trường | Ghi chú |
|---|---|
| `client_name`, `project_name` | Hiện ở đầu trang kết quả |
| `detected_priority_note` | Câu giải thích khách coi trọng điều gì, ghi rõ là suy luận của AI |
| `requirements[]` | `id` (REQ-001…), `short_label` (1–2 từ, hiện trên dải phủ), `text`, `is_hard_constraint`, `source_section`, `source_quote` |

`short_label` là trường frontend thêm vào so với schema của analyst — cần nó để vẽ
dải phủ. Tối đa khoảng 14 ký tự.

`is_hard_constraint: true` được đánh dấu ◆ trên giao diện: đây là ràng buộc mà vi
phạm thì không thể khuyến nghị gửi đi.

### 2.2 `confirmed_criteria[]`

```json
{ "name": "Completeness vs RFP Requirements", "key": "completeness_vs_rfp",
  "description": "...", "weight": 3, "origin": "base",
  "why": "...", "source_refs": [{ "section": "Requirements", "quote": "..." }] }
```

| Trường | Ghi chú |
|---|---|
| `key` | Khoá dùng trong `evaluation.scores`; 7 khoá gốc theo Appendix A |
| `weight` | **Số**, do analyst đề xuất. Frontend chỉ hiển thị, không tính lại |
| `origin` | `base` · `rfp_explicit` · `ai_inferred` · `user` |
| `why` | Vì sao tiêu chí này có mặt và nặng như vậy |

### 2.3 `evaluation`

| Trường | Ghi chú |
|---|---|
| `overall_score` | 1–5, backend tự tính theo trọng số |
| `recommendation` | `ready` · `revise` · `do_not_accept_as_written` |
| `summary` | 1–2 câu, không mở đầu bằng nhãn khuyến nghị vì UI đã hiện |
| `scores` | map `key → điểm nguyên 1–5` |
| `rationales` | map `key → câu nhận xét` |
| `criterion_citations` | map `key → danh sách trích dẫn` |
| `requirements[]` | `id`, `status`, `status_label`, `rfp_quote`, `response_quote`, `searched_terms`, `rationale` |
| `findings[]` | `id`, `requirement_ids[]`, `kind`, `severity`, `rfp_quote`, `response_quote`, `searched_terms`, `rationale`, `suggested_fix` |

**`status`**: `met` · `partial` · `missing` · `contradicted` · `unsubstantiated`.
Hai giá trị cuối đều hiển thị bằng nền kẻ sọc màu tím.

**`kind`**: `strength` · `missing` · `vague` · `contradiction` ·
`unsupported_promise` · `risk_disclosure`.

**`severity`**: `critical` · `major` · `minor` · `info`. Frontend sắp xếp
findings theo thứ tự này.

**Quy tắc khuyến nghị** (theo `rubric.json` của benchmark): vi phạm một ràng buộc
cứng thì không được `ready`, kể cả khi điểm trung bình cao.

### 2.4 Trích dẫn

Mọi `*_quote` phải **trùng nguyên văn** tài liệu gốc. Frontend so khớp chuỗi sau
khi chuẩn hoá khoảng trắng, gạch ngang và dấu nháy, rồi tô vàng đúng đoạn. Không
tìm thấy thì không có gì sáng lên, và người dùng sẽ thấy ngay.

Backend **phải tự kiểm tra** trước khi trả về; không khớp thì bỏ finding đó.

Khi kết luận là proposal không nhắc gì, để `response_quote: null` và điền
`searched_terms` — frontend hiện "Nothing in the proposal matches this".

---

## 3. Lỗi

```json
{ "detail": "GEMINI_API_KEY chua duoc cau hinh" }
```

Dùng HTTP 4xx/5xx kèm `detail`; frontend hiện nguyên câu đó cho người dùng.

Khi gọi thất bại mà tài liệu đang là một trong 4 mẫu, frontend tự hiện kết quả lưu
sẵn kèm nhãn "Stored sample result", nên demo không bao giờ chết giữa chừng.

---

## 4. Cần thống nhất

- **Thời gian**: frontend chờ đến khi có kết quả, không timeout, nhưng màn chạy
  giữ tối thiểu 3,6 giây để 5 bước pipeline kịp hiện. Nên giữ tổng dưới 30 giây.
- **PDF**: hiện frontend chặn upload PDF. Backend đã có `/v1/markitdown` chuyển
  PDF/PPTX sang Markdown; khi nối vào thì sửa `frontend/src/api/review.js`.
- **Ngôn ngữ**: nội dung trả về đang là tiếng Anh vì người dùng cuối là sales của
  FPT Software Europe.
