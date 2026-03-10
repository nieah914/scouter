# Task: Initial Setup & Project Structure
우리는 "현대인 생존 전투력 측정기"라는 웹서비스의 MVP를 개발할 거야.
아래에 명시된 기술 스택과 디렉토리 구조 원칙을 정확히 지켜서 **초기 보일러플레이트(Boilerplate) 코드와 폴더 구조**를 생성해 줘.

## 1. Tech Stack
- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **Frontend:** Jinja2 Templates, HTML5, Tailwind CSS (CDN), HTMX (CDN)
- **Database:** Supabase (supabase-py)
- **Environment:** .env 기반 환경변수 관리 (python-dotenv)

## 2. Directory Structure Rule
반드시 아래의 'MVP 최적화 모놀리식 구조'를 따라야 해. React나 Next.js 관련 파일은 절대 만들지 마.

survival-calculator-mvp/
├── main.py                 # FastAPI 진입점 및 앱 실행
├── .env.example            # 환경변수 템플릿 (DB, API Key 등)
├── requirements.txt        # 패키지 의존성 목록
│
├── /app                    # 백엔드 핵심 로직
│   ├── __init__.py
│   ├── config.py           # 환경변수 로딩 (Pydantic BaseSettings)
│   ├── /routers            # 라우터
│   │   ├── pages.py        # Jinja2 HTML 서빙용 엔드포인트
│   │   └── api.py          # HTMX 비동기 통신용 API 엔드포인트
│   ├── /services           # 비즈니스 로직
│   │   ├── ai.py           # OpenAI API 호출 로직
│   │   ├── stats.py        # 공공데이터 백분위 및 캐릭터 산식
│   │   └── payment.py      # 결제 검증 로직
│   ├── /models             # 데이터 스키마
│   │   └── schemas.py      # Pydantic 모델
│   └── /database           # DB 연결
│       └── db_client.py    # Supabase 연결 설정
│
├── /templates              # 프론트엔드 (Jinja2)
│   ├── base.html           # Tailwind CSS 및 HTMX CDN이 포함된 베이스 껍데기
│   ├── index.html          # 메인 랜딩 (base.html을 상속)
│   └── /components         # HTMX로 교체될 조각 화면들 (비워둬도 됨)
│       ├── landing.html
│       ├── step_form.html
│       ├── loading.html
│       └── result.html
│
└── /static                 # 정적 파일
    ├── /css
    │   └── style.css       # 픽셀 폰트 등 커스텀 스타일
    └── /images             # 이미지 폴더

## 3. Action Required
1. 위 디렉토리 구조를 생성하는 터미널 명령어(Bash/Shell) 스크립트를 작성해 줘.
2. `requirements.txt`에 필요한 필수 패키지 목록을 작성해 줘.
3. FastAPI 앱을 실행하기 위한 가장 기본이 되는 `main.py`와 `app/config.py`의 코드를 작성해 줘.
