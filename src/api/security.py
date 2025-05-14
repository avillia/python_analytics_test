from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, PyJWTError, decode
from starlette.datastructures import URL

from config import JWT_ALGORITHM, JWT_SECRET_KEY

bearer_scheme = HTTPBearer(auto_error=False)


def extract_token_from(credentials: HTTPAuthorizationCredentials) -> str | None:
    if not credentials or credentials.scheme.lower() != "bearer":
        return None
    return credentials.credentials


def extract_payload_from(jwt_token: str) -> dict:
    try:
        return decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )


def extract_root_route(url: URL) -> str:
    """aka convert e.g '/receipts/regenerate?as_pdf=True&omit_nulls=False' -> 'receipts'"""
    return url.path.lstrip("/").split("/", 1)[0]


def extract_info_about_current(request: Request) -> tuple[str, str]:
    method = request.method.upper()
    path_segment = extract_root_route(request.url)
    return method, path_segment


def build_set_of_permissions_required_to_perform(
    request_method: str,
    *,
    at: str,
) -> set[str]:
    path_segment = at
    # I wish I was able to use itertools.product here,
    # but since product() produces sequence,
    # I would require yet another set comprehension to build all those strings anyway,
    # so I decided to go without product()
    return {
        f"{method}@{path}"
        for method in ("*", request_method)
        for path in ("*", path_segment)
    }


def extract_accesses_from(payload: dict[str, list[str]]) -> set[str]:
    return set(payload.pop("access", []))


def is_possible_to_perform_request_based_on(
    method: str,
    path_segment: str,
    payload: dict,
):
    required_permissions = build_set_of_permissions_required_to_perform(
        method, at=path_segment
    )
    accesses = extract_accesses_from(payload)

    # I hope this part confuses no one, but in case it does:
    # Here I check whether intersection of two sets
    # (required_permissions & accesses, hence the 'and' symbol here)
    # is not empty (that means that token contains entry
    # that matches access entry required to make this request)

    if required_permissions & accesses:
        return True
    return False


async def authorize_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = extract_token_from(credentials)
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = extract_payload_from(token)
    method, path_segment = extract_info_about_current(request)

    if is_possible_to_perform_request_based_on(method, path_segment, payload):
        return payload

    raise HTTPException(
        status_code=403,
        detail=f"Not enough permissions. "
        f"You need to be able to make '{method}@{path_segment}' to access this resource!",
    )
