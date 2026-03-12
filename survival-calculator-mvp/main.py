import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import pages, api

app = FastAPI(title="현대인 생존 전투력 측정기")

# 절대경로 사용 (Vercel 서버리스 환경 호환)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "public", "static")), name="static")

# 라우터 등록
app.include_router(pages.router)
app.include_router(api.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
