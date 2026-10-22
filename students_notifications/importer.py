import csv
from collections.abc import Iterable
from pathlib import Path

import openpyxl

from .db import get_duplicate_keys, upsert_student
from .models import Student
from .validators import (
    normalize_email,
    normalize_name,
    normalize_sexo,
    validate_email,
    validate_phone,
)

REQUIRED_COLUMNS = [
    "control",
    "apaterno",
    "amaterno",
    "nombre",
    "email_int",
    "correo_per",
    "sexo",
    "telefono",
]


def _normalize_row(row: dict[str, str]) -> Student:
    return Student(
        control=row["control"].strip(),
        apaterno=normalize_name(row["apaterno"]),
        amaterno=normalize_name(row["amaterno"]),
        nombre=normalize_name(row["nombre"]),
        email_int=normalize_email(row["email_int"]),
        correo_per=normalize_email(row["correo_per"]),
        sexo=normalize_sexo(row["sexo"]),
        telefono=row["telefono"].strip().replace(" ", "").replace("-", ""),
    )


def _validate_headers(headers: Iterable[str]) -> list[str]:
    normalized_headers = [header.strip().lower() for header in headers if header is not None]
    missing = [column for column in REQUIRED_COLUMNS if column not in normalized_headers]
    return missing


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        headers = [field.strip().lower() for field in reader.fieldnames or []]
        missing = _validate_headers(headers)
        if missing:
            raise ValueError(f"Archivo CSV faltan columnas: {', '.join(missing)}")
        return [
            {key.strip().lower(): (value or "") for key, value in row.items()}
            for row in reader
        ]


def _read_xlsx(path: Path) -> list[dict[str, str]]:
    workbook = openpyxl.load_workbook(path, data_only=True)
    worksheet = workbook.active
    rows = list(worksheet.iter_rows(values_only=True))
    if not rows:
        raise ValueError("El archivo XLSX está vacío")
    headers = [str(value).strip().lower() if value is not None else "" for value in rows[0]]
    missing = _validate_headers(headers)
    if missing:
        raise ValueError(f"Archivo XLSX faltan columnas: {', '.join(missing)}")
    key_map = dict(enumerate(headers))
    return [
        {key_map[col]: str(cell or "") for col, cell in enumerate(row)}
        for row in rows[1:]
    ]


def import_students(path: str) -> tuple[int, int, list[str]]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError("Archivo no encontrado")
    if file_path.suffix.lower() == ".csv":
        rows = _read_csv(file_path)
    elif file_path.suffix.lower() in {".xlsx", ".xls"}:
        rows = _read_xlsx(file_path)
    else:
        raise ValueError("Formato de archivo no soportado")

    inserted = 0
    skipped = 0
    logs: list[str] = []

    for index, row in enumerate(rows, start=2):
        try:
            student = _normalize_row(row)
            if not student.control:
                raise ValueError("El control es obligatorio")
            if not validate_email(student.email_int):
                raise ValueError("email_int inválido")
            if not validate_email(student.correo_per):
                raise ValueError("correo_per inválido")
            if not validate_phone(student.telefono):
                raise ValueError("telefono inválido")
            if get_duplicate_keys(student):
                raise ValueError("El registro ya existe por control, email o teléfono")
            upsert_student(student)
            inserted += 1
        except Exception as error:
            skipped += 1
            logs.append(f"Fila {index}: {error}")
            continue

    return inserted, skipped, logs
