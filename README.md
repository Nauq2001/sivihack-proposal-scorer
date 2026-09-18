# SiviHack Starter Kit

Bo khung san sang: React (frontend) + FastAPI (backend) + Google AI Studio (Gemini) da noi san.
Muc tieu: sang mai nhan de xong chi viec sua logic/UI theo bai toan that, khong mat thoi gian setup lai tu dau.

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
- Key Gemini co limit $100 cho ca doi — dung `gemini-2.0-flash` (nhe, re) khi dev/test, chi doi model manh hon (`gemini-1.5-pro` neu can) luc lam tinh nang quan trong nhat.
- Voucher n8n Cloud Pro (neu can workflow automation): kich hoat theo huong dan BTC gui, ma la `2026-COMMUNITY-HACKATHON-FRANKFURT-9AA2EB02`.

## 5. Khi nhan de bai ngay mai

1. Doc de, xac dinh: input gi, output gi, AI dong vai tro gi trong luong (chatbot? phan loai? tao noi dung? RAG?).
2. Sua prompt/logic trong `backend/main.py` (ham `call_ai` / them endpoint moi).
3. Sua giao dien trong `frontend/src/App.jsx` cho dung use case that.
4. Uu tien lam 1 luong end-to-end chay duoc truoc (dau vao -> AI -> hien ket qua), roi moi lam dep UI hay them tinh nang phu.

## 6. Frontend Proposal Scorer

`frontend/` khong con la demo goi AI nua, no la app that voi 3 buoc:

1. **Documents** - dan hoac upload RFP + proposal (.md/.txt)
2. **Criteria** - bang 4 cot: High, Medium, Low, Don't score. Moi cot co mot cau
   chu thich giai thich muc do anh huong toi diem. 7 tieu chi goc theo Appendix A,
   cong them tieu chi AI doc duoc tu RFP. The chi hien ten, bam vao moi mo mo ta +
   ly do + trich dan. Keo tha hoac bam mui ten de doi cot, them/xoa tieu chi
3. **Review** - diem tong, dai trang thai 9 yeu cau RFP, de xuat sua cho tung loi,
   va khung nguon ben phai: bam vao trich dan la doan goc duoc to vang

App goi `POST /api/review`. Khi backend chua chay, no tu dung ket qua luu san cho
4 proposal mau va hien nhan "Stored sample result", nen demo khong bao gio chet.

Quy tac mau: trang **Criteria khong dung mau** (muc do noi bang chu High/Medium/Low
kem chu thich). Mau chi dung o trang **Review**, voi mot nghia duy nhat la
**do = xu ly truoc tien**: yeu cau bi thieu/mau thuan, hoac tieu chi dang keo diem
xuong nhieu nhat.

App goi 2 endpoint: `POST /api/criteria` (doc RFP ra tieu chi) va `POST /api/review`.

Hop dong API cho backend/AI: `docs/api/review-contract.md`
Du lieu mau (response that): `frontend/src/mocks/*.json`
Request mau: `docs/api/samples/request.example.json`

## 7. De bai & du lieu mau

- De bai Track 1 (Proposal Scorer - FPT Software Europe): `docs/challenge/track-1-proposal-scorer.pdf`
- RFP + 4 proposal mau + vi du output: `docs/challenge/sample_data/`

