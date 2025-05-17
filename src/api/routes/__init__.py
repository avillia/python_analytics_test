from src.api.routes.auth import auth_router
from src.api.routes.product import product_router
from src.api.routes.receipts import receipt_router

routers = (
    auth_router,
    receipt_router,
)
