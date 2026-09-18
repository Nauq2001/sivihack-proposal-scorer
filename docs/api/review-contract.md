# Hợp đồng API — `/api/criteria` và `/api/review`

Tài liệu này mô tả dữ liệu mà frontend gửi đi và dữ liệu mà backend phải trả về.
Frontend đã chạy được với hợp đồng này: khi chưa có backend, nó đọc các file mẫu
trong `frontend/src/mocks/` — đó chính là response thật, không phải bản rút gọn.

Có hai endpoint:

| Endpoint | Khi nào gọi | Trả về |
|---|---|---|
| `POST /api/criteria` | Người dùng mở màn Criteria với một RFP mới | Danh sách tiêu chí + mức ưu tiên đề xuất, đọc từ RFP |
| `POST /api/review` | Bấm "Run review" | Điểm, trạng thái từng yêu cầu, đề xuất sửa |

- Frontend: `frontend/src/api/review.js`
- Dữ liệu mẫu `/api/criteria`: `frontend/src/mocks/criteria_nordframe.json`
- Dữ liệu mẫu `/api/review`: `frontend/src/mocks/response_1_weak.json`, `response_2_medium.json`,
  `response_3_strong.json`, `response_4_overpromise.json`
- Request mẫu: `docs/api/samples/request.example.json`

Bắt buộc: backend trả về JSON đúng khoá và đúng kiểu như dưới đây. Thiếu khoá thì
frontend sẽ hỏng. Thừa khoá thì frontend bỏ qua, không sao.

---

## 1. `POST /api/criteria` — đọc RFP ra tiêu chí

Request: `{ "rfp": { "name": "rfp_nordframe.md", "text": "..." } }`

Response:

```json
{
  "schema_version": "1.0",
  "meta": { "rfp_name": "rfp_nordframe.md", "model": "gemini-2.0-flash", "generated_at": "...", "duration_ms": 4200 },
  "criteria": [
    {
      "id": "comp",
      "name": "Completeness vs. RFP",
      "description": "Every explicit RFP requirement is addressed.",
      "source": "base",
      "suggested_priority": "high",
      "why": "The RFP lists seven numbered requirements and puts each one in bold...",
      "citations": [ { "source": "rfp", "found": true, "label": "RFP, Requirements", "quote": "Requirements" } ]
    },
    {
      "id": "accuracy",
      "name": "Data accuracy & validation",
      "description": "Says how inventory figures are checked against reality before anyone relies on them.",
      "source": "ai",
      "suggested_priority": "medium",
      "why": "The RFP does not list this as a requirement, but it gives the reason behind Requirement 7...",
      "citations": [ { "source": "rfp", "found": true, "label": "RFP, Req. 7", "quote": "inventory decisions will be made based on this system" } ]
    }
  ]
}
```

| Trường | Ghi chú |
|---|---|
| `source` | `base` = 7 tiêu chí gốc theo Appendix A (`pu`, `scope`, `price`, `time`, `comp`, `tone`, `risk`) · `ai` = tiêu chí AI đọc thêm từ RFP này |
| `suggested_priority` | `high` · `medium` · `low` · `skip`. Hệ số tương ứng 3 · 2 · 1 · 0, nhưng **giao diện không hiện số** — người dùng chỉ thấy tên mức kèm một câu chú thích |
| `why` | 1–2 câu **giải thích vì sao đặt ở mức đó**. Người dùng đọc câu này ngay trên thẻ, nên phải nói được điều gì trong RFP dẫn tới mức ưu tiên |
| `citations` | Trích dẫn RFP chứng minh cho `why`, cùng quy tắc ở mục 3.4 |

**Luôn trả đủ 7 tiêu chí `base`**, kể cả khi RFP không nói gì nhiều về chúng (khi đó
đặt `low` và để `citations` rỗng — xem `tone` trong file mẫu: RFP không nhắc gì tới
văn phong nên không có trích dẫn nào, đừng bịa ra một câu cho có). Tiêu chí `ai` là phần thêm: chỉ đề xuất khi **thật sự có căn cứ trong
RFP** và **chưa được 7 tiêu chí gốc phủ**. Hai ví dụ trong file mẫu:

- `accuracy` — RFP giải thích lý do của Req. 7: quyết định tồn kho dựa trên hệ thống này
- `legacy` — hệ thống cũ chỉ xuất hiện ở phần Background, không nằm trong 7 yêu cầu
  đánh số, nên checklist sẽ bỏ sót

Đề xuất 0–3 tiêu chí `ai` là hợp lý. Bịa ra tiêu chí không có trong RFP (ví dụ GDPR
khi RFP không nhắc) là lỗi nặng hơn là không đề xuất gì.

Người dùng có thể kéo thẻ sang cột khác, xoá thẻ, hoặc tự thêm thẻ
(`source: "custom"`). Frontend giữ lựa chọn đó và gửi lại trong `/api/review`.

---

## 2. `POST /api/review` — Request

```json
{
  "rfp":      { "name": "rfp_nordframe.md", "text": "# Request for Proposal ..." },
  "proposal": { "name": "response_1_weak.md", "text": "# Proposal: ..." },
  "criteria": [
    { "id": "comp",     "name": "Completeness vs. RFP",      "description": "...", "priority": "high", "source": "base" },
    { "id": "accuracy", "name": "Data accuracy & validation","description": "...", "priority": "medium",   "source": "ai" },
    { "id": "gdpr",     "name": "GDPR & data residency",     "description": "...", "priority": "low",       "source": "custom" }
  ]
}
```

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `rfp.text`, `proposal.text` | string | Markdown hoặc plain text. Hiện chưa gửi PDF |
| `criteria[].id` | string | 7 id gốc, cộng với id của tiêu chí `ai` và `custom` người dùng giữ lại |
| `criteria[].priority` | `high` \| `medium` \| `low` \| `skip` | Cột người dùng đang để thẻ đó |
| `criteria[].source` | `base` \| `ai` \| `custom` | |

**Chấm đủ mọi tiêu chí trong mảng, kể cả `skip`.** `skip` nghĩa là người dùng không
muốn tính vào điểm, nhưng vẫn muốn đọc nhận xét. Tiêu chí `custom` do người dùng tự
viết, chỉ có `name` và `description` — vẫn phải chấm và trích dẫn như các tiêu chí khác.

**Priority dùng để làm gì:** chỉ là ngữ cảnh cho backend. Điểm tổng do frontend tự
tính lại từ `criteria[].score`, nên kéo thẻ là điểm đổi ngay, không gọi API lại.

---

## 3. `POST /api/review` — Response

```json
{
  "schema_version": "1.0",
  "meta": {
    "rfp_name": "rfp_nordframe.md",
    "proposal_name": "response_1_weak.md",
    "model": "gemini-2.0-flash",
    "generated_at": "2026-09-17T09:00:00Z",
    "duration_ms": 11800
  },
  "overall": {
    "score": 1.67,
    "verdict": "not_ready",
    "summary": "Pricing and timeline are both deferred, four of the seven RFP requirements are never mentioned..."
  },
  "client_priorities": [ { "id": "priority-1", "title": "...", "text": "...", "suggestion": "...", "citations": [] } ],
  "criteria":    [ { "id": "pu", "name": "...", "description": "...", "priority": "low", "score": 3, "comment": "...", "citations": [] } ],
  "requirements":[ { "id": "r3", "short_label": "PostgreSQL", "name": "...", "ask": "...", "rfp_citation": {}, "status": "missing", "status_label": "Missing", "finding": "...", "suggested_fix": "...", "citations": [] } ],
  "other_issues":[ { "id": "other-1", "status": "partial", "label": "Generic", "title": "...", "finding": "...", "suggested_fix": "...", "citations": [] } ]
}
```

### 3.1 `overall`

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `score` | number 1–5 | Trung bình có trọng số: high ×3, medium ×2, low ×1, skip ×0 |
| `verdict` | `not_ready` (<2.5) \| `revise` (<4) \| `ready` (≥4) | |
| `summary` | string | 1–2 câu, nêu lý do chính. Không mở đầu bằng "Not ready to send" vì UI đã hiện nhãn đó |

### 3.2 `criteria` — đúng số lượng và thứ tự như trong request

`score` là số nguyên 1–5. `comment` là 1–2 câu **cụ thể**, có dẫn chiếu tên mục.
"Thiếu bảng giá chi tiết" đạt. "Cần rõ ràng hơn" không đạt.

### 3.3 `requirements` — 9 phần tử, đúng thứ tự này

`r1` Dashboard · `r2` Low-stock alerts · `r3` PostgreSQL · `r4` Access roles ·
`r5` Rollout plan · `r6` Support SLAs · `r7` Risks · `budget` Budget · `timeline` Timeline

Bảy mục `r1`–`r7` là 7 yêu cầu đánh số trong RFP; `budget` và `timeline` là hai
ràng buộc cứng. Với RFP khác, số lượng và `id` sẽ khác — frontend đọc theo mảng,
không hard-code.

| Trường | Ghi chú |
|---|---|
| `short_label` | 1–2 từ, hiện trong dải trạng thái. Tối đa khoảng 14 ký tự |
| `ask` | Yêu cầu của khách, viết lại một câu |
| `rfp_citation` | Trích dẫn tới chỗ RFP nêu yêu cầu này |
| `status` | `met` \| `partial` \| `missing` \| `conflict` |
| `status_label` | Nhãn ngắn hiện trên badge: `Addressed`, `Vague`, `Missing`, `Contradicts`, `Deferred`, `No dates`, `Unrealistic`… |
| `finding` | Vì sao lại xếp trạng thái đó |
| `suggested_fix` | `null` khi `status` là `met`. Ngược lại **bắt buộc** có: câu chữ viết sẵn để dán vào proposal, không phải lời khuyên chung chung |
| `clarification` | Tuỳ chọn, dùng khi mục đã đạt nhưng còn điểm cần làm rõ. Gồm `title`, `text`, `suggested_fix`, `citations` |

### 3.4 `citations` — phần quan trọng nhất

```json
{ "source": "proposal", "found": true,  "label": "Proposal, Pricing", "quote": "Pricing will be provided upon further discussion" }
{ "source": "rfp",      "found": true,  "label": "RFP, Req. 3",       "quote": "no migration to a new database" }
{ "source": "proposal", "found": false, "label": "Proposal: not found", "searched_terms": ["PostgreSQL"] }
```

**Quy tắc bắt buộc với bên AI:**

1. `quote` phải **trùng nguyên văn** một đoạn trong tài liệu gốc. Frontend tìm
   chuỗi con để bôi vàng, sau khi chuẩn hoá khoảng trắng, dấu gạch ngang
   (`–`, `—` → `-`) và dấu nháy (`’` → `'`). Không được rút gọn, diễn đạt lại hay
   thêm `...`.
2. **Backend phải tự kiểm tra** `quote` có nằm trong text hay không trước khi trả
   về. Không tìm thấy thì bỏ trích dẫn đó, hoặc bỏ luôn nhận định nếu nó dựa hoàn
   toàn vào trích dẫn sai. Một câu trích bịa làm mất niềm tin vào cả bản đánh giá,
   và giám khảo sẽ thử bằng bộ dữ liệu lạ.
3. `quote` nên ngắn, khoảng 3–12 từ, đủ để định vị.
4. Khi kết luận là "proposal không nhắc gì", dùng dạng `found: false` kèm
   `searched_terms` — những từ đã tìm. Frontend hiện: "No mention of X anywhere in
   the proposal."
5. `label` là những gì người dùng đọc: `"RFP, Req. 6"`, `"Proposal, Pricing"`.

### 3.5 `client_priorities`

Đọc từ RFP, không liên quan proposal: mỗi phần tử nêu một điều khách coi trọng, kèm
trích dẫn để người dùng kiểm chứng. Phần gợi ý mức ưu tiên cho từng tiêu chí đã
chuyển sang `/api/criteria`, mục này chỉ còn là phần giải thích cho người đọc.

---

## 4. Thang điểm 1–5 (mô tả neo cho prompt)

Cần định nghĩa rõ từng mức, nếu không cùng một proposal chấm hai lần sẽ ra hai điểm.

| Điểm | Pricing clarity | Timeline clarity |
|---|---|---|
| 1 | Không có con số, hoặc "báo giá sau" | Không có mốc nào |
| 2 | Chỉ có khoảng giá, hoặc tổng tiền không breakdown | Có tên giai đoạn, không có ngày |
| 3 | Tổng tiền và breakdown một phần | Có mốc nhưng không khớp deadline của RFP |
| 4 | Breakdown từng hạng mục, trong ngân sách, còn một điểm mơ hồ | Mốc cụ thể, còn một khoảng chưa rõ |
| 5 | Breakdown đủ, trong ngân sách, đủ mọi khoản RFP yêu cầu | Mốc cụ thể, khớp đủ deadline của RFP |

**`comp` (Completeness) nên tính bằng công thức, không để AI chấm cảm tính:**

```
tỉ lệ = (số met × 1 + số partial × 0.5) / tổng số yêu cầu r1..rN
score = round(1 + 4 × tỉ lệ)
nếu có bất kỳ requirement nào status = "conflict" thì score tối đa = 2
```

Kiểm chứng với dữ liệu mẫu: weak 1.5/7 → 2 · medium 4.5/7 → 4 · strong 7/7 → 5 ·
overpromise (có conflict) → tối đa 2.

---

## 5. Lỗi

```json
{ "detail": "GEMINI_API_KEY chưa được cấu hình" }
```

Dùng HTTP 4xx/5xx kèm `detail`. Frontend hiện nguyên câu trong `detail` cho người
dùng, nên viết câu người đọc hiểu được, kèm cách xử lý.

Khi gọi API thất bại và tài liệu đang là một trong 4 mẫu, frontend tự động hiện
kết quả lưu sẵn kèm nhãn "Stored sample result", để demo không bao giờ chết giữa
chừng.

---

## 6. Cần thống nhất khi làm

- **Thời gian phản hồi.** Frontend chờ cho đến khi có kết quả, không timeout.
  Nên giữ dưới 20 giây; nếu lâu hơn thì phải bàn để chuyển sang dạng streaming.
- **Thứ tự `requirements`** chính là thứ tự hiển thị. Riêng `criteria` được frontend
  sắp lại theo cột, nên thứ tự trong response không quan trọng.
- **PDF.** Hiện frontend chặn upload PDF. Nếu backend nhận PDF thì đổi request
  thành `multipart/form-data`, báo trước để sửa `frontend/src/api/review.js`.
- **Ngôn ngữ đầu ra.** Toàn bộ nội dung đang là tiếng Anh vì người dùng cuối là
  nhân viên sales của FPT Software Europe. Nếu đổi thì đổi cả UI.
