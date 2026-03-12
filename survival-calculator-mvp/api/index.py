import sys
import os

# 상위 디렉토리(survival-calculator-mvp/)를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
