"""
HTML 페이지 서빙 라우터 (Jinja2 Templates)
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Jinja2 커스텀 필터
def format_number(value):
    """숫자를 천 단위 콤마로 포맷"""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)

templates.env.filters["format_number"] = format_number


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/result", response_class=HTMLResponse)
async def result_page(request: Request, token: str = ""):
    """결과 공유 링크 전용 풀페이지 (브라우저 직접 접근용)"""
    return templates.TemplateResponse("result_page.html", {
        "request": request,
        "token": token,
    })


@router.get("/battle", response_class=HTMLResponse)
async def battle_page(request: Request, challenger: str = ""):
    """친구 배틀 풀페이지"""
    return templates.TemplateResponse("battle_page.html", {
        "request": request,
        "challenger": challenger,
    })
