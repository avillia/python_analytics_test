from os import getenv

DATABASE_URL = getenv("DATABASE_URL", "sqlite:///:memory:")
CRYPTO_PEPPER = getenv("CRYPTO_PEPPER", "test-secret")
JWT_SECRET_KEY = getenv("JWT_SECRET_KEY", "test-secret")
JWT_ALGORITHM = getenv("JWT_ALGORITHM", "HS256")
