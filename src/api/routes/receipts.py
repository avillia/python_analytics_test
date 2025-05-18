from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.api.security import requires_authorization
from src.core.handlers.receipts.get import (
    render_as_str_receipt_with,
    retrieve_if_is_possible_to_look_data_for,
)

receipt_router = APIRouter(
    prefix="/receipts",
    tags=["receipts"],
    responses={404: {"description": "Not found"}},
)


class ReceiptResponse(BaseModel):
    class Config:
        from_attributes = True


class PaymentType(StrEnum):
    cash = "cash"
    cashless = "cashless"


class ProductItem(ReceiptResponse):
    name: str
    price: Decimal
    quantity: Decimal


class PaymentInfo(ReceiptResponse):
    type: PaymentType
    amount: Decimal


class ReceiptCreate(BaseModel):
    products: list[ProductItem]
    payment: PaymentInfo


class ProductItemResponse(ReceiptResponse):
    total: Decimal


class PaymentInfoResponse(PaymentInfo): ...


class ReceiptGetResponse(ReceiptResponse):
    id: str
    products: list[ProductItemResponse]
    payment: PaymentInfoResponse
    total: Decimal
    rest: Decimal
    created_at: datetime


class ReceiptListItem(ReceiptResponse):
    id: str
    total: Decimal
    payment_type: PaymentType
    created_at: datetime


class ReceiptCollection(BaseModel):
    count: int
    receipts: list[ReceiptListItem]


@receipt_router.post("/", response_model=ReceiptResponse, status_code=201)
async def create_receipt(receipt_data: ReceiptCreate) -> ReceiptResponse: ...


@receipt_router.get("/", response_model=ReceiptCollection)
async def fetch_own_receipts(
    user_id: requires_authorization,
    created_after: datetime | None = Query(None),
    created_before: datetime | None = Query(None),
    min_total: Decimal | None = Query(None),
    max_total: Decimal | None = Query(None),
    payment_type: PaymentType | None = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ReceiptCollection: ...


@receipt_router.get("/{receipt_id}", response_model=ReceiptResponse)
async def fetch_receipt_by_id(receipt_id: str) -> ReceiptResponse: ...


@receipt_router.get("/{receipt_id}/text", response_model=dict)
async def fetch_receipt_as_text(
    receipt_id: str,
    chars_per_line: int | None = Query(32, ge=20, le=100),
) -> dict[str, str]:
    try:
        return {
            "receipt_id": receipt_id,
            "receipt": render_as_str_receipt_with(receipt_id, chars_per_line),
        }
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"No receipt for id={receipt_id} found in db!",
        )
