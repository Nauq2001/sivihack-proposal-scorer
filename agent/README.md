# RFP Analyst

MVP cho luồng Proposal Scorer:

```text
RFP.md -> Gemini structured extraction -> RFPAnalysis
       -> criteria review state -> ScoringInput JSON
```

RFP Analyst trích atomic requirements, hard constraints, citations, metadata, base/custom criteria packets và `detected_priority_note`. Criterion do người dùng thêm chỉ cần tên, mô tả và weight tùy chọn. Resolver tự kiểm tra trùng; bản trùng dùng criterion chuẩn và thay weight bằng weight người dùng vừa đặt. Không tìm được thông tin trong RFP thì giữ nội dung người dùng, để links rỗng và ghi note cho scorer.

## Cài đặt

Yêu cầu Python 3.11+ và `uv`.

```bash
cd /Users/faze/Documents/Codex/2026-09-17/let/outputs/rfp-analyst
uv sync --extra dev --no-editable
```

Sau bước này, dùng `uv run --no-sync ...` hoặc gọi trực tiếp `.venv/bin/rfp-analyst ...`. Cờ `--no-sync` giữ wheel vừa cài; nếu gọi `uv run` không có cờ này, uv có thể tự đổi project về editable mode trước khi chạy.

API call thật dùng `GOOGLE_API_KEY` (ưu tiên) hoặc `GEMINI_API_KEY`. Không đặt key trong repository:

```bash
export GOOGLE_API_KEY="YOUR_KEY"
export GEMINI_MODEL="gemini-3.8-flash"
```

## Test nhanh không cần API key

```bash
uv run --no-sync pytest
```

Expected: toàn bộ tests pass. Tests dùng fake structured model để kiểm tra đúng một model call, backend cấp IDs, citation validation, duplicate/weight, fallback ngoài RFP, edit state và packaging.

Validate fixture NordFrame và tạo review state:

```bash
uv run --no-sync rfp-analyst validate \
  --analysis fixtures/nordframe-analysis.json \
  --rfp fixtures/rfp_nordframe.md

mkdir -p work
uv run --no-sync rfp-analyst start-review \
  --analysis fixtures/nordframe-analysis.json \
  --rfp fixtures/rfp_nordframe.md \
  --output work/review.json
```

Thử thêm criterion ngoài RFP bằng safe fallback, không gọi AI:

```bash
uv run --no-sync rfp-analyst add-criterion \
  --state work/review.json \
  --name "Đào tạo nhân viên kho" \
  --description "Proposal cần có kế hoạch đào tạo cho nhân viên kho." \
  --weight 3 \
  --offline \
  --output work/review-with-training.json
```

Mở `work/review-with-training.json` và kiểm tra:

- name/description/weight vẫn đúng input;
- packet có `origin: "user"`;
- `requirement_ids` và `source_refs` rỗng;
- note bắt đầu bằng `USER_DEFINED_NOT_RFP`.

Thử duplicate và weight replacement:

```bash
uv run --no-sync rfp-analyst add-criterion \
  --state work/review.json \
  --name "pricing clarity" \
  --description "Giá phải rõ ràng." \
  --weight 4 \
  --offline \
  --output work/review-duplicate.json
```

Expected terminal: `MERGED: Pricing Clarity weight=4`. File chỉ có một `Pricing Clarity`, dùng description/packet chuẩn và weight 4.

Đóng gói cho Scoring Agent:

```bash
uv run --no-sync rfp-analyst package \
  --state work/review-with-training.json \
  --proposal fixtures/response_1_weak.md \
  --output work/scoring-input.json

uv run --no-sync rfp-analyst schema --output work/scoring-input.schema.json
```

`work/scoring-input.json` có đúng bốn top-level fields: `rfp_analysis`, `raw_rfp_text`, `raw_proposal_text`, `confirmed_criteria`.

Bản contract/fixture đã đóng gói sẵn để gửi teammate:

- `contracts/scoring-input.schema.json`
- `fixtures/nordframe-scoring-input.example.json`

## Live test Gemini

Sau khi export API key:

```bash
uv run --no-sync rfp-analyst analyze \
  --rfp fixtures/rfp_nordframe.md \
  --output work/live-analysis.json

uv run --no-sync rfp-analyst validate \
  --analysis work/live-analysis.json \
  --rfp fixtures/rfp_nordframe.md
```

Review `work/live-analysis.json` theo checklist:

- `client_name` là NordFrame Logistics GmbH và `project_name` bám title;
- requirements bao phủ dashboard, alerts, PostgreSQL/no migration, role access, onboarding, support/SLA, risks, budget và hai milestones;
- quote là substring chính xác của RFP;
- không tự đặt latency, SLA number hoặc ngày tuyệt đối;
- `detected_priority_note` được ghi rõ là inference, có nguồn, hoặc null;
- bảy base criterion names giữ nguyên canonical spelling.

Backend sẽ tự reconcile khác biệt xuống dòng/khoảng trắng trong quote model trả về về đúng substring nguyên văn của RFP; quote khác nội dung vẫn bị từ chối.

Test semantic duplicate/enrichment với Gemini bằng cách bỏ `--offline` khỏi `add-criterion`. Nếu model/enrichment lỗi, criterion vẫn được giữ với `ENRICHMENT_FAILED`; initial RFP analysis thì fail closed, không xuất contract không đáng tin. Nếu bạn chỉnh source code, chạy lại `uv sync --extra dev --no-editable`, sau đó dùng `uv run --no-sync` để cập nhật wheel trong môi trường.

## CLI

- `analyze`: gọi Gemini một lần bằng native structured output.
- `validate`: kiểm tra exact citations, IDs, mappings và packets.
- `start-review`: tạo state mà FE/backend có thể sửa.
- `add-criterion`, `edit-criterion`, `remove-criterion`: mô phỏng human-in-loop.
- `package`: đóng băng snapshot đầu vào scorer.
- `schema`: export JSON Schema trực tiếp từ models đang chạy.

Mặc định CLI không overwrite file. Dùng `--overwrite` khi chủ động thay file cũ.

## Contract với Scoring Agent

Scorer dùng `confirmed_criteria`, không dùng suggested weights để ghi đè lựa chọn user. Mọi RFP requirement vẫn phải có finding khi criterion tương ứng bị tắt. Completeness đọc toàn bộ findings. Hard constraint bị contradicted phải được backend scorer ép severity high. Missing có proposal citation rỗng. Overall score tính bằng code.

`client_name`, `project_name` và `detected_priority_note` nằm trong `rfp_analysis`; scorer echo hai tên sang output. Priority note chỉ là context Level 3, không đổi weights hoặc tạo requirements.

## Nguồn API đã đối chiếu

- LangChain `ChatGoogleGenerativeAI`: `langchain-google-genai`, `GOOGLE_API_KEY`/`GEMINI_API_KEY`, native `with_structured_output(..., method="json_schema")`.
- Google Gemini models: model ID mặc định `gemini-3.8-flash`.
