from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.api.security import requires_authorization
from src.core.handlers.receipts.get import (
    convert_to_dict_repr,
    render_as_str_receipt_with,
    retrieve_if_is_possible_to_look_data_for,
    retrieve_user_receipts_data,
)
from src.core.handlers.receipts.post import store_receipt_by

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
    is_cashless_payment: bool
    amount: Decimal


class ReceiptCreate(BaseModel):
    products: list[ProductItem]
    payment: PaymentInfo


class ProductItemResponse(ReceiptResponse):
    total: Decimal


class PaymentInfoResponse(PaymentInfo): ...


class SingleReceiptResponse(ReceiptResponse):
    id: str
    items: list[ProductItemResponse]
    payment: PaymentInfoResponse
    total: Decimal
    rest: Decimal
    created_at: datetime


class Pagination(BaseModel):
    starting: int
    ending: int
    count: int


class ReceiptCollection(BaseModel):
    pagination: Pagination
    receipts: list[SingleReceiptResponse]
    total: int


@receipt_router.post("/", response_model=SingleReceiptResponse, status_code=201)
async def create_receipt(
    user_id: requires_authorization,
    receipt_data: ReceiptCreate,
) -> SingleReceiptResponse:
    fresh_receipt = store_receipt_by(receipt_data, user_id)
    return SingleReceiptResponse.model_validate(convert_to_dict_repr(fresh_receipt))


@receipt_router.get("/", response_model=ReceiptCollection)
async def fetch_own_receipts(
    user_id: requires_authorization,
    created_after: datetime | None = Query(None),
    created_before: datetime | None = Query(None),
    min_total: Decimal | None = Query(None),
    max_total: Decimal | None = Query(None),
    is_cashless_operation: bool | None = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ReceiptCollection:

    optional_filters: dict = {
        "created_after": created_after,
        "created_before": created_before,
        "min_total": min_total,
        "max_total": max_total,
        "payment_type": is_cashless_operation,
    }
    filters = {k: v for k, v in optional_filters.items() if v is not None}

    filters["user_id"] = user_id
    filters["limit"] = limit
    filters["offset"] = offset

    total, receipts = retrieve_user_receipts_data(filters)

    pagination = Pagination(
        starting=offset,
        ending=min(offset + limit, total),
        count=len(receipts),
    )

    return ReceiptCollection(
        pagination=pagination,
        total=total,
        receipts=[SingleReceiptResponse.model_validate(receipt) for receipt in receipts],
    )


@receipt_router.get("/{receipt_id}", response_model=SingleReceiptResponse)
async def fetch_receipt_by_id(
    user_id: requires_authorization,
    receipt_id: str,
) -> SingleReceiptResponse:
    try:
        receipt_from_db = retrieve_if_is_possible_to_look_data_for(
            receipt_id, using=user_id
        )
        return SingleReceiptResponse.model_validate(receipt_from_db)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"No receipt for id={receipt_id} found in db!",
        )
    except AssertionError:
        raise HTTPException(
            status_code=403,
            detail=f"You have no permission to access sensitive data!",
        )


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
