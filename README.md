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

## 6. De bai & du lieu mau

- De bai Track 1 (Proposal Scorer - FPT Software Europe): `docs/challenge/track-1-proposal-scorer.pdf`
- RFP + 4 proposal mau + vi du output: `docs/challenge/sample_data/`
- Tom tat de va quy uoc cho Claude: `CLAUDE.md`

## 7. Bo cong cu Claude Code cho team (thiet ke / frontend)

Da cau hinh san trong repo, khong can cai tay:

- `.claude/settings.json` — plugin: `frontend-design`, `typescript-lsp`, `gitlab`
- `.mcp.json` — MCP server: `chrome-devtools` (xem & chup man hinh UI), `playwright`,
  `context7` (tra docs thu vien), `figma-talk`
- `.claude/skills/ui-build-verify` — quy trinh Figma -> code -> kiem tra tren Chrome

Lan dau mo repo bang `claude`: bam **Trust** thu muc, dong y cai marketplace/plugin va
bat MCP server khi duoc hoi. Can Node 18+ (MCP chay qua `npx`).
Figma chinh thuc la connector claude.ai — moi nguoi tu bat trong Settings > Connectors.
