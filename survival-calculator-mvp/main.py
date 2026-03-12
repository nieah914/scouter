"""
로컬 개발 전용 실행 파일
- Vercel 배포 진입점: api/index.py
- 로컬 실행: uvicorn main:app --reload --port 8000
"""
from api.index import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
