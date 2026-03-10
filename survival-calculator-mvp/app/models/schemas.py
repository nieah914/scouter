"""
Pydantic 스키마 정의
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class GenderEnum(str, Enum):
    M = "M"
    F = "F"


class UserInput(BaseModel):
    """유저 폼 입력 데이터"""
    user_token: str
    gender: GenderEnum
    age: int = Field(ge=15, le=80)
    height: float = Field(ge=140.0, le=220.0)
    weight: float = Field(ge=30.0, le=200.0)
    sleep_hours: float = Field(ge=2.0, le=12.0)
    pushup_count: int = Field(ge=0, le=200)
    running_count: int = Field(ge=0, le=150, description="셔틀런 횟수")
    coffee_cups: int = Field(ge=0, le=20)
    overtime_days: int = Field(ge=0, le=7)


class StepSubmit(BaseModel):
    """단계별 폼 제출 데이터"""
    step: int
    user_token: str
    # 단계별 값 (해당 단계에만 값이 있음)
    gender: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    sleep_hours: Optional[float] = None
    pushup_count: Optional[int] = None
    running_count: Optional[int] = None
    coffee_cups: Optional[int] = None
    overtime_days: Optional[int] = None


class PaymentSuccess(BaseModel):
    """결제 성공 콜백 파라미터"""
    paymentKey: str
    orderId: str
    amount: int
    user_token: str
