# Hợp đồng API — `/api/analyse` và `/api/score`

Frontend chạy **một chiều ba màn**: tài liệu → tiêu chí → kết quả, giữa mỗi màn là
một màn tiến trình. Hai endpoint khớp đúng hai agent trong `AI/`:

| Endpoint | Agent | Trả về |
|---|---|---|
| `POST /api/analyze-rfp` | RFP Analyst | `rfp_analysis` + `confirmed_criteria` |
| `POST /api/score` | Proposal Analyst | `scoring` |

Màn Criteria là **bước người dùng duyệt**: kéo thả giữa bốn cột, thêm, xoá.
Mức ưu tiên ban đầu lấy từ `recommended_priority` trong `AI/contracts.py`.

Khi bấm chấm, frontend gửi `confirmed_criteria` **đã chỉnh**, đúng như contract
mô tả: *"the single source of truth for which criteria to score and at what
weight, after the human checkpoint"*.

| Cột | `weight` gửi đi |
|---|---|
| High | 3 |
| Medium | 2 |
| Low | 1 |

Không muốn chấm tiêu chí nào thì **xoá hẳn** khỏi bảng; không có cột "để sang một
bên", vì contract bắt `weight > 0`. Tiêu chí người dùng tự thêm có `origin: "user"`.

Route `/api/analyze-rfp` gửi thêm `requirement_ids` cho mỗi tiêu chí, lấy từ
`criterion_packets`, để thẻ hiện được nó kiểm tra những yêu cầu nào.

- Frontend gọi: `frontend/src/api/review.js`
- Dữ liệu mẫu (chính là response thật): `frontend/src/mocks/response_*.json`
- Hình dạng bám theo `agent/contracts/scoring-input.schema.json` của RFP Analyst
  và `proposal_scorer_benchmark/evaluation_output.schema.json` của phần chấm điểm.

---

## 1. Request

`POST /api/analyze-rfp`:

```json
{ "raw_rfp_text": "# Request for Proposal ..." }
```

`POST /api/score` — đúng `ScoringInput` trong `AI/contracts.py`:

```json
{
  "rfp_analysis": { },
  "raw_rfp_text": "...",
  "raw_proposal_text": "...",
  "confirmed_criteria": [ ]
}
```

Tên endpoint và hình dạng lấy từ `CLAUDE.md` mục "Interface contract" của nhánh AI.

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

Nhãn này lấy **số mà chính RFP đánh** cho dòng chứa `source_quote` ("3." trong
danh sách ⇒ `Req 3`), nên người đọc dò ngược lại tài liệu gốc được. Một dòng RFP
tách ra hai yêu cầu thì hai nhãn trùng nhau — đúng, cả hai cùng trỏ về một chỗ.
Dòng không đánh số thì quay về `source_section` (`Budget 1`, `Timeline 2`).

`/api/score` đổi luôn mọi `REQ-0NN` trong `verdict`, `criteria[].comment`,
`findings[].reason` và `findings[].suggested_patch` sang nhãn này: số thứ tự nội
bộ không có nghĩa gì với người đọc RFP.

`is_hard_constraint: true` được đánh dấu ◆ trên giao diện: đây là ràng buộc mà vi
phạm thì không thể khuyến nghị gửi đi.

### 2.2 `confirmed_criteria[]` (`CriterionWeight`)

```json
{ "name": "Completeness vs RFP Requirements", "description": "...", "weight": 3,
  "recommended_priority": "high", "priority_reason": "...",
  "origin": "base", "source_refs": [{ "source_section": "Requirements", "quote": "..." }] }
```

| Trường | Ghi chú |
|---|---|
| `name` | **Khoá nối** sang `scoring.criteria[].name`, phải trùng từng ký tự |
| `weight` | Số, do analyst đề xuất. Frontend chỉ hiển thị |
| `recommended_priority` | `high` · `medium` · `low` → ba cột trên màn Criteria |
| `priority_reason` | Câu giải thích hiện trong thẻ khi mở ra |
| `origin` | `base` · `rfp_explicit` · `ai_inferred` · `user`, lấy từ `criterion_packets` |

### 2.3 `scoring` (`ScoringResult`)

| Trường | Ghi chú |
|---|---|
| `overall_score` | 1–5, backend tính theo trọng số (`compute_overall_score`) |
| `verdict` | Câu kết luận, hiện ở khối điểm |
| `recommendation` | `ready` · `revise` · `do_not_accept_as_written` — trường frontend cần thêm ngoài `ScoringResult` |
| `criteria[]` | `name`, `score` (1–5), `comment`, `citations[]` là **mảng chuỗi** |
| `findings[]` | `requirement_id` (một mã), `status`, `severity`, `reason`, `citation`, `suggested_patch` |

**`status`**: `met` · `missing` · `vague` · `contradicted` (bốn giá trị trong
`AI/contracts.py`).

**`severity`**: `high` · `medium` · `low`. Frontend sắp xếp findings theo thứ tự này.

Mỗi requirement nên có đúng một finding, kể cả khi `met` — frontend vẽ dải phủ
từ danh sách này.

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
