from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

receipt_router = APIRouter(
    prefix="/receipts",
    tags=["receipts"],
    responses={404: {"description": "Not found"}},
)


class PaymentType(StrEnum):
    cash = "cash"
    cashless = "cashless"


class ProductItem(BaseModel):
    name: str
    price: Decimal
    quantity: Decimal


class PaymentInfo(BaseModel):
    type: PaymentType
    amount: Decimal
    additional_info: Optional[str] = None


class ReceiptCreate(BaseModel):
    products: List[ProductItem]
    payment: PaymentInfo


class ProductItemResponse(ProductItem):
    total: Decimal


class PaymentInfoResponse(PaymentInfo): ...


class ReceiptResponse(BaseModel):
    id: str
    products: List[ProductItemResponse]
    payment: PaymentInfoResponse
    total: Decimal
    rest: Decimal
    created_at: datetime


class ReceiptListItem(BaseModel):
    id: str
    total: Decimal
    payment_type: PaymentType
    created_at: datetime


class ReceiptCollection(BaseModel):
    count: int
    receipts: List[ReceiptListItem]


@receipt_router.post("/", response_model=ReceiptResponse, status_code=201)
async def create_receipt(receipt_data: ReceiptCreate) -> ReceiptResponse: ...


@receipt_router.get("/", response_model=ReceiptCollection)
async def fetch_own_receipts(
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    min_total: Optional[Decimal] = Query(None),
    max_total: Optional[Decimal] = Query(None),
    payment_type: Optional[PaymentType] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ReceiptCollection: ...


@receipt_router.get("/{receipt_id}", response_model=ReceiptResponse)
async def fetch_receipt_by_id(receipt_id: str) -> ReceiptResponse: ...


@receipt_router.get("/{receipt_id}/text", response_model=str)
async def fetch_receipt_as_text(
    receipt_id: str,
    chars_per_line: Optional[int] = Query(40, ge=10, le=100),
) -> str: ...
