import sqlite3
import sys
from pathlib import Path

from .models import Student
from .validators import normalize_email


def _get_app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

DB_PATH = _get_app_root() / "notificaciones.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                control TEXT PRIMARY KEY,
                apaterno TEXT NOT NULL,
                amaterno TEXT NOT NULL,
                nombre TEXT NOT NULL,
                email_int TEXT NOT NULL UNIQUE,
                correo_per TEXT NOT NULL UNIQUE,
                sexo TEXT NOT NULL,
                telefono TEXT NOT NULL UNIQUE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        connection.commit()


def upsert_student(student: Student) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO students (control, apaterno, amaterno, nombre, email_int, correo_per, sexo, telefono)
            VALUES (:control, :apaterno, :amaterno, :nombre, :email_int, :correo_per, :sexo, :telefono)
            ON CONFLICT(control) DO UPDATE SET
                apaterno=excluded.apaterno,
                amaterno=excluded.amaterno,
                nombre=excluded.nombre,
                email_int=excluded.email_int,
                correo_per=excluded.correo_per,
                sexo=excluded.sexo,
                telefono=excluded.telefono
            """,
            {
                **student.as_dict(),
                "email_int": normalize_email(student.email_int),
                "correo_per": normalize_email(student.correo_per),
            },
        )
        connection.commit()


def delete_student(control: str) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM students WHERE control = ?", (control.strip(),))
        connection.commit()


def list_students() -> list[Student]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM students ORDER BY apaterno, amaterno, nombre").fetchall()
    return [Student(**dict(row)) for row in rows]


def get_student(control: str) -> Student | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM students WHERE control = ?", (control.strip(),)).fetchone()
    return Student(**dict(row)) if row else None


def field_exists(field: str, value: str) -> bool:
    if field not in {"control", "email_int", "correo_per", "telefono"}:
        raise ValueError("Unsupported field for existence check")
    query = f"SELECT 1 FROM students WHERE {field} = ? LIMIT 1"
    normalized_value = normalize_email(value) if field in {"email_int", "correo_per"} else value.strip()
    with get_connection() as connection:
        row = connection.execute(query, (normalized_value,)).fetchone()
    return row is not None


def save_config(key: str, value: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO config (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value.strip()),
        )
        connection.commit()


def get_config(key: str, default: str | None = None) -> str | None:
    with get_connection() as connection:
        row = connection.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
    return row[0] if row else default


def get_all_config() -> dict[str, str]:
    with get_connection() as connection:
        rows = connection.execute("SELECT key, value FROM config").fetchall()
    return {row[0]: row[1] for row in rows}


def get_duplicate_keys(student: Student) -> list[str]:
    return [
        field
        for field in ["control", "email_int", "correo_per", "telefono"]
        if field_exists(field, getattr(student, field))
    ]
