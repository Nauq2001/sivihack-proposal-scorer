from fastapi import APIRouter

import backend.app.v1.endpoints.MarkitDown.router as markdown_v1_router

router = APIRouter()

router.include_router(markdown_v1_router, prefix="/markitdown")