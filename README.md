# SiviHack Starter Kit

Bo khung san sang: React (frontend) + FastAPI (backend) + Google AI Studio (Gemini) da noi san.
Muc tieu: sang mai nhan de xong chi viec sua logic/UI theo bai toan that, khong mat thoi gian setup lai tu dau.

## 0. Chay ban demo hoan chinh (nhanh `main`)

```bash
# Terminal 1 - backend
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 - frontend
cd frontend && npm install && npm run dev
```

`curl localhost:8000/api/health` cho biet module nao da san sang.

| Endpoint | Tu nhanh | Trang thai |
|---|---|---|
| `/api/health` | — | OK |
| `/v1/markitdown/...` | be-init | OK, chuyen PDF/PPTX sang Markdown |
| `/rag/retrieve` | rag/development | OK, 168 ban ghi tham chieu |
| `/api/evidence/*` | rag-enterprise | OK, kho doanh nghiep + kiem tra loi hua |
| `/api/analyze-rfp` | feat/ai | OK, RFP Analyst (~11-13s) |
| `/api/score` | feat/ai | OK, Proposal Analyst (~13-16s) |

Hai route nam o `backend/review_routes.py`, chi la lop noi: nap `AI/` va
`agent/src`, goi ham co san, doi loi thanh HTTP. Logic cham diem van o nhanh AI.

Can `GEMINI_API_KEY` trong `backend/.env`. **`gemini-2.0-flash` da bi Google go
khoi API**; ca app dung `gemini-3.8-flash` (xem `.env.example`).

Khi backend chua chay, frontend dung ket qua luu san cho 4 proposal mau va hien
nhan "Stored sample result".

## 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# File .env da co san API key Gemini BTC cap - kiem tra lai truoc khi chay
uvicorn main:app --reload --port 8000
```

Test nhanh:
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

Mo http://localhost:5173 — go thu 1 cau vao o nhap, bam Gui, se thay cau tra loi tu Gemini.

## 3. Doi provider AI (neu can)

Sua trong `backend/.env`:
- `AI_PROVIDER=gemini` (mac dinh, dung key BTC cap, limit $100)
- `AI_PROVIDER=anthropic` (can dien them `ANTHROPIC_API_KEY`)

Khong sua code, chi sua file `.env`.

## 4. Luu y bao mat

- File `.env` da nam trong `.gitignore` — KHONG commit len Git, KHONG paste key vao Slack/Discord/Zalo cong khai.
- Key Gemini co limit $100 cho ca doi. `gemini-2.0-flash` da bi go khoi API; hien dung `gemini-3.8-flash` cho ca hai agent.
- Voucher n8n Cloud Pro (neu can workflow automation): kich hoat theo huong dan BTC gui, ma la `2026-COMMUNITY-HACKATHON-FRANKFURT-9AA2EB02`.

## 5. Khi nhan de bai ngay mai

1. Doc de, xac dinh: input gi, output gi, AI dong vai tro gi trong luong (chatbot? phan loai? tao noi dung? RAG?).
2. Sua prompt/logic trong `backend/main.py` (ham `call_ai` / them endpoint moi).
3. Sua giao dien trong `frontend/src/App.jsx` cho dung use case that.
4. Uu tien lam 1 luong end-to-end chay duoc truoc (dau vao -> AI -> hien ket qua), roi moi lam dep UI hay them tinh nang phu.

## 6. Frontend Proposal Scorer

Luong mot chieu ba man, giua moi man la mot man tien trinh:

1. **Documents** - dan hoac upload RFP + proposal, hoac chon 1 trong 4 mau
2. *(tien trinh)* RFP Analyst doc RFP
3. **Criteria** - tieu chi do AI chot, chia ba cot High/Medium/Low theo
   `recommended_priority`. Chi xem, khong sua; mo the de doc ly do va trich dan
4. *(tien trinh)* Proposal Analyst cham diem
5. **Result** - khuyen nghi + diem, dai phu yeu cau (danh dau rang buoc cung),
   diem tung tieu chi, findings kem cau sua, khung nguon tra cuu trich dan

## 7. De bai & du lieu mau

- De bai Track 1 (Proposal Scorer - FPT Software Europe): `docs/challenge/track-1-proposal-scorer.pdf`
- RFP + 4 proposal mau + vi du output: `docs/challenge/sample_data/`

