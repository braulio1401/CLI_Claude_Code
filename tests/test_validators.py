from students_notifications.validators import (
    normalize_email,
    normalize_name,
    normalize_sexo,
    validate_email,
    validate_phone,
)


def test_normalize_name_and_sexo() -> None:
    assert normalize_name("eduardo alberto") == "Eduardo Alberto"
    assert normalize_name("  ochoa  ") == "Ochoa"
    assert normalize_sexo("masculino") == "Masculino"
    assert normalize_sexo("FEMENINO") == "Femenino"
    assert normalize_sexo("otro") == "Otro"


def test_normalize_email_and_validators() -> None:
    assert normalize_email("TeSt@DomAIn.COM") == "test@domain.com"
    assert validate_email("alumno@example.com")
    assert not validate_email("malformed-email")
    assert validate_phone("+521234567890")
    assert validate_phone("1234567890")
    assert not validate_phone("123-abc-7890")
