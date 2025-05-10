from fastapi import APIRouter
from pydantic import BaseModel

product_router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)


class Product(BaseModel):
    id: str
    name: str
    description: str | None = None
    price: float
    tags: list[str] = []


class ProductCollection(BaseModel):
    count: int
    products: list[Product]


@product_router.get("/", response_model=ProductCollection)
async def fetch_all_products_from_db() -> tuple[int, list[object]]: ...


@product_router.get("/{product_id}", response_model=Product)
async def fetch_specific_product_from_db(product_id: str) -> object: ...


@product_router.post("/", response_model=Product, status_code=201)
async def create_new_product_in_db(product_data: Product) -> object: ...


@product_router.put("/{product_id}", response_model=Product)
async def update_specific_product(product_id: str, product_data: Product) -> object: ...


@product_router.delete("/{product_id}", status_code=204)
async def delete_specific_product(product_id: str) -> None:...
