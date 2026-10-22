import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_ALLOWED = re.compile(r"^\+?[0-9]{7,15}$")


def normalize_name(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    return " ".join(part.capitalize() for part in text.replace("  ", " ").split())


def normalize_sexo(value: str) -> str:
    text = value.strip().lower()
    if not text:
        return ""
    if text.startswith("m"):
        return "Masculino"
    if text.startswith("f"):
        return "Femenino"
    if text.startswith("o"):
        return "Otro"
    return text.capitalize()


def normalize_email(value: str) -> str:
    return value.strip().lower()


def validate_email(value: str) -> bool:
    return bool(EMAIL_REGEX.match(value.strip()))


def validate_phone(value: str) -> bool:
    text = value.strip().replace(" ", "").replace("-", "")
    return bool(PHONE_ALLOWED.match(text))
