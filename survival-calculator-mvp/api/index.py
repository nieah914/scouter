import os
import sys

# 프로젝트 루트를 Python 경로에 추가 (Vercel 서버리스 환경)
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import pages, api as api_router

app = FastAPI(title="현대인 생존 전투력 측정기")

# 정적 파일 (로컬: FastAPI 서빙 / Vercel: public/ CDN이 우선)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(_root, "public", "static")),
    name="static",
)

# 라우터 등록
app.include_router(pages.router)
app.include_router(api_router.router, prefix="/api")
