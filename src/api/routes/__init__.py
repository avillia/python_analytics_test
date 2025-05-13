from src.api.routes.auth import auth_router
from src.api.routes.product import product_router

routers = (
    auth_router,
    product_router,
)
