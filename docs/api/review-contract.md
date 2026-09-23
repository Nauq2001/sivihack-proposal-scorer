# Hợp đồng API — `/api/analyse` và `/api/score`

Frontend chạy **một chiều ba màn**: tài liệu → tiêu chí → kết quả, giữa mỗi màn là
một màn tiến trình. Hai endpoint khớp đúng hai agent trong `AI/`:

| Endpoint | Agent | Trả về |
|---|---|---|
| `POST /api/analyze-rfp` | RFP Analyst | `rfp_analysis` + `confirmed_criteria` |
| `POST /api/score` | Proposal Analyst | `scoring` |
| `POST /api/create-ticket` | — (n8n) | `{ ticket_key, ticket_url }` |

`/api/create-ticket` không phải bước thứ ba của pipeline — người dùng tự bấm nút
**"Send to Work"** ở màn kết quả khi muốn nhờ team review, không tự động chạy sau
`/api/score`. Xem mục 5.

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

Tên endpoint và hình dạng lấy từ `docs/architecture.md` mục "Interface contract" của nhánh AI.

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

## 2.4 `POST /api/confirm-criteria` — chốt tiêu chí

Gọi **một lần**, ngay trước `/api/score`, không phải mỗi lần người dùng thêm tiêu
chí. Người dùng thêm/xoá/kéo thả thoải mái ở màn 2 mà không tốn lượt gọi model
nào; bấm "Score the proposal" mới là lúc chốt.

```json
{ "rfp_analysis": {...}, "raw_rfp_text": "...", "criteria": [ ... ] }
→ { "confirmed_criteria": [...], "rfp_analysis": {...}, "merges": [...], "warnings": [...] }
```

Route dựng lại `CriteriaState` của agent rồi chạy resolver
(`agent/src/rfp_analyst/criteria.py`) cho **riêng** các tiêu chí `origin: "user"`:

- **gộp trùng nghĩa** — `merges: [{added, merged_into}]`, frontend báo cho người dùng;
- **enrichment** — nối tiêu chí tự thêm vào `requirement_ids`/`source_refs` có thật
  trong RFP, để nó không bị chấm mù. Không có gì trong RFP đỡ thì để rỗng kèm ghi
  chú `USER_DEFINED_NOT_RFP`.

Chi phí: **0 giây khi không ai thêm tiêu chí** (không gọi model), khoảng 9 giây cho
mỗi tiêu chí tự thêm.

`add_or_merge` gọi lại `apply_priority_recommendations`, tức đề xuất của AI ghi đè
cột người dùng vừa chọn. Route đặt lại lựa chọn của người dùng **sau cùng**: cột họ
chốt là cuối cùng.

Route hỏng ở bất kỳ đâu cũng không chặn được bước chấm: frontend dùng đúng danh
sách người dùng đã chọn kèm packet dự phòng, và hiện một câu cảnh báo.

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

---

## 5. `POST /api/create-ticket` — nút "Send to Work"

Không phải bước thứ ba của pipeline hai agent — nút riêng ở màn kết quả
(`ResultView.jsx`, cạnh trái nút "Start over"), người dùng tự bấm khi muốn nhờ
team review qua Jira + Slack. `AI/scoring.py::score_proposal()` không gọi cái
này tự động.

**Request**: chính object `scoring` (`ScoringResult`) frontend đã có sẵn trong
state — gửi thẳng, không map lại field:

```json
{ "client_name": "...", "project_name": "...", "overall_score": 2.3,
  "verdict": "...", "criteria": [ ], "findings": [ ] }
```

**Response 200**:

```json
{ "ticket_key": "SCORE-123", "ticket_url": "https://<workspace>.atlassian.net/browse/SCORE-123" }
```

Shape này do workflow n8n (Webhook → Jira → Slack) trả về, không phải
`AI/n8n_client.py` tự định nghĩa — khớp đúng field nào thì `ticket.ticket_key`/
`ticket.ticket_url` phía `TicketButton` mới hiển thị đúng.

**Lỗi**: cùng convention mục 3 — `502` kèm `detail` nếu không gọi được webhook
hoặc webhook trả lỗi; `503` nếu thiếu `N8N_TICKET_WEBHOOK_URL` trong `.env`.

Backend chỉ import `AI/n8n_client.py::send_to_jira_slack_workflow()` — hàm này
lọc `findings` còn `severity != "low"` trước khi gửi, để ticket Jira gọn, không
liệt kê mọi finding `met`.
