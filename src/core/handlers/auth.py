from datetime import datetime, timedelta
from hashlib import sha256
from hmac import compare_digest

from jwt import encode

from config import CRYPTO_PEPPER, JWT_ALGORITHM, JWT_SECRET_KEY
from src.core.db.managers import (
    AccessManager,
    DBAppConfigManager,
    RoleManager,
    UserManager,
)
from src.core.utils import generate_alphanumerical_id


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


def retrieve_data_depending_on(login: str, plain_password: str) -> str:
    user_manager = UserManager()
    user = user_manager.lookup_for_user_by(login)
    if user is None:
        raise LookupError(f"No such user [{login}] exists in db!")

    if not are_passwords_matching(plain_password, user.id, user.password_hash):
        raise KeyError(f"Wrong password for user [{login}]! Try again!")

    return user.id


def generate_jwt_token_for(user_id: str) -> str:
    config = DBAppConfigManager()
    expire = datetime.now() + timedelta(minutes=config["ACCESS_TOKEN_EXPIRE_MINUTES"])

    token = encode(
        payload={"sub": user_id, "exp": expire},
        key=JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    return token


def obtain_jwt_token_for(login: str, plain_password: str) -> str:
    user = retrieve_data_depending_on(login, plain_password)
    return generate_jwt_token_for(user)


def grant_all_the_accesses_for(new_user_id: str):
    admin_role_id = RoleManager().ensure_role_exists("admin")

    RoleManager().assign(new_user_id, admin_role_id)
    AccessManager().grant_unlimited_access_to(admin_role_id)


def grant_basic_accesses_for(new_user_id: str):
    user_role_id = RoleManager().ensure_role_exists("user")

    RoleManager().assign(new_user_id, user_role_id)
    AccessManager().grant(user_role_id, permission_to_perform="GET", at="/receipts")
    AccessManager().grant(user_role_id, permission_to_perform="POST", at="/receipts")


def create_new_user_with_following(
    login: str,
    email: str,
    name: str,
    plain_password: str,
):
    user_manager = UserManager()
    is_user_already_exists = user_manager.lookup_for_user_by(login)
    if is_user_already_exists:
        raise KeyError(f"User with such {login=} already exists!")

    new_user_id = generate_alphanumerical_id()
    password_hash = hash_password(plain_password, new_user_id)
    user_manager.create_new_user_using(new_user_id, login, name, email, password_hash)

    is_first_user_ever = user_manager.fetch_total_user_count() < 0
    if is_first_user_ever:
        grant_all_the_accesses_for(new_user_id)
    grant_basic_accesses_for(new_user_id)


def assign_existing_role_with(role_name: str, *, to: str) -> bool:
    login = to
    user = UserManager().lookup_for_user_by(login)
    if user is None:
        raise LookupError(f"No such user [{login}] exists in db!")

    role_manager = RoleManager()
    role = role_manager.lookup_for_role_by(role_name)
    if role is None:
        raise LookupError(f"No such role [{role_name}] exists in db!")

    return role_manager.assign(user.id, role.id)
