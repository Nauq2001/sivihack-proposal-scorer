# Bộ khung dự án SiviHack

Bộ khung gồm React (frontend), FastAPI (backend) và kết nối Google AI Studio (Gemini). Mục tiêu là chuẩn bị sẵn môi trường để đội tập trung sửa logic và giao diện theo đề bài.

## 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Kiểm tra API key Gemini do ban tổ chức cấp trong .env trước khi chạy
uvicorn main:app --reload --port 8000
```

Kiểm tra nhanh:

```bash
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Xin chao"}'
```

## 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Mở http://localhost:5173 để sử dụng giao diện Proposal Scorer, gồm ba bước mô tả ở mục 6.

## 3. Đổi nhà cung cấp AI

Sửa trong `backend/.env`:

- `AI_PROVIDER=gemini`: mặc định, dùng key ban tổ chức cấp; ngân sách được ghi nhận trong dự án là 100 USD cho cả đội.
- `AI_PROVIDER=anthropic`: cần điền thêm `ANTHROPIC_API_KEY`.

Việc chọn nhà cung cấp được cấu hình qua `.env`.

## 4. Lưu ý bảo mật và cấu hình

- File `.env` đã nằm trong `.gitignore`; không commit hoặc chia sẻ công khai API key.
- Cấu hình mẫu hiện dùng `gemini-2.0-flash`. Kiểm tra model được tài khoản hỗ trợ và hạn mức thực tế trước khi sử dụng.
- Nếu dùng n8n Cloud Pro để tự động hóa luồng công việc, kích hoạt voucher theo hướng dẫn của ban tổ chức: `2026-COMMUNITY-HACKATHON-FRANKFURT-9AA2EB02`.

## 5. Hướng phát triển từ bộ khung

1. Xác định đầu vào, đầu ra và vai trò của AI trong bài toán.
2. Sửa prompt hoặc logic tại `backend/main.py`, gồm hàm `call_ai` hoặc endpoint mới.
3. Sửa giao diện tại `frontend/src/App.jsx` theo nhu cầu.
4. Ưu tiên luồng hoạt động xuyên suốt từ đầu vào đến AI và hiển thị kết quả, rồi mới bổ sung giao diện hay tính năng phụ.

## 6. Giao diện Proposal Scorer

`frontend/` gồm ba bước:

1. **Documents (Tài liệu):** dán hoặc tải lên RFP và proposal dạng `.md`/`.txt`.
2. **Criteria (Tiêu chí):** chọn trọng số Low/Medium/High (thấp/trung bình/cao) cho sáu tiêu chí của giao diện hiện tại, kèm gợi ý từ RFP.
3. **Review (Đánh giá):** xem điểm tổng, trạng thái chín yêu cầu của RFP mẫu, gợi ý sửa và tài liệu nguồn. Bấm trích dẫn để tô vàng đoạn gốc.

Ứng dụng gọi `POST /api/review`. Khi gọi API thất bại với một trong bốn cặp tài liệu mẫu chưa chỉnh sửa, ứng dụng dùng kết quả lưu sẵn và hiện nhãn “Stored sample result” (kết quả mẫu đã lưu).

- Hợp đồng API giao diện hiện tại: [review-contract.md](docs/api/review-contract.md).
- Kết quả mẫu: `frontend/src/mocks/*.json`.
- Dữ liệu gửi mẫu: `docs/api/samples/request.example.json`.

## 7. Đề bài và dữ liệu mẫu

- Đề Track 1, Proposal Scorer của FPT Software Europe: `docs/challenge/track-1-proposal-scorer.pdf`.
- RFP, bốn proposal và ví dụ đầu ra: `docs/challenge/sample_data/`.
- Ví dụ đầu ra bằng tiếng Anh: [scoring_example.md](docs/challenge/sample_data/scoring_example.md).

## 8. Scoring RAG

Toàn bộ hướng dẫn sử dụng, tích hợp Python, kiểm thử và tài liệu thiết kế RAG nằm trong [backend/rag/README.md](backend/rag/README.md).

