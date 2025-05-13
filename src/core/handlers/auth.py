from hashlib import sha256
from hmac import compare_digest
from datetime import datetime, timedelta

from jwt import encode

from src.core.db.managers import UserManager, DBAppConfigManager
from config import CRYPTO_PEPPER


def hash_password(plain_password: str, salt: str) -> str:
    data = f"{salt}:{plain_password}:{CRYPTO_PEPPER}".encode("utf-8")
    return sha256(data).hexdigest()


def are_passwords_matching(
    plain_password: str,
    password_salt: str,
    hash_from_db: str,
) -> bool:
    computed_hash = hash_password(plain_password, password_salt)
    return compare_digest(computed_hash, hash_from_db)


def retrieve_data_depending_on(
    login: str,
    plain_password: str,
) -> tuple[str, list[str]]:
    user_manager = UserManager()
    user = user_manager.lookup_for_user_by(login)
    if user is None:
        raise LookupError(f"No such user [{login}] exists in db!")

    if not are_passwords_matching(plain_password, user.id, user.password_hash):
        raise KeyError(f"Wrong password for user [{login}]! Try again!")

    user_id = user.id
    accesses_as_str = [
        f"{access.allowed_method}@{access.route_url}"
        for access in user_manager.gather_all_accesses_for(user_id)
    ]

    return user_id, accesses_as_str


def generate_jwt_token_for(user_id: str, accesses: list[str]) -> str:
    config = DBAppConfigManager()
    expire = datetime.now() + timedelta(minutes=config["ACCESS_TOKEN_EXPIRE_MINUTES"])
    payload = {
        "sub": user_id,
        "exp": expire,
        "access": accesses,
    }

    token = encode(payload, config["JWT_SECRET_KEY"], algorithm=config["JWT_ALGORITHM"])
    return token


def obtain_jwt_token_for(login: str, plain_password: str) -> str:
    user, accesses = retrieve_data_depending_on(login, plain_password)
    return generate_jwt_token_for(user, accesses)
