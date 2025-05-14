from string import ascii_letters, digits
from random import choices


def generate_alphanumerical_id(length: int = 12) -> str:
    return "".join(choices(ascii_letters + digits, k=length))
