import csv
from pathlib import Path

import openpyxl

from students_notifications import db, importer
from students_notifications.db import init_db


def test_import_csv_and_skip_invalid(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "notificaciones.db"
    monkeypatch.setattr(db, "DB_PATH", database_path)
    monkeypatch.setattr(db, "get_connection", lambda: __import__("sqlite3").connect(database_path))
    init_db()

    csv_path = tmp_path / "students.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "control",
            "apaterno",
            "amaterno",
            "nombre",
            "email_int",
            "correo_per",
            "sexo",
            "telefono",
        ])
        writer.writerow(["2025001", "Ochoa", "Lopez", "Eduardo Alberto", "eduardo@uni.edu", "eduardo.personal@gmail.com", "Masculino", "+521234567890"])
        writer.writerow(["", "Perez", "Garcia", "Ana", "ana@uni.edu", "ana.personal@gmail.com", "Femenino", "1234567890"])

    inserted, skipped, logs = importer.import_students(str(csv_path))
    assert inserted == 1
    assert skipped == 1
    assert any("Fila 3" in entry for entry in logs)


def test_import_xlsx_headers_validation(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "notificaciones.db"
    monkeypatch.setattr(db, "DB_PATH", database_path)
    monkeypatch.setattr(db, "get_connection", lambda: __import__("sqlite3").connect(database_path))
    init_db()

    xlsx_path = tmp_path / "students.xlsx"
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.append([
        "control",
        "apaterno",
        "amaterno",
        "nombre",
        "email_int",
        "correo_per",
        "sexo",
        "telefono",
    ])
    worksheet.append(["2025002", "Martinez", "Sanchez", "Luis", "luis@uni.edu", "luis.personal@gmail.com", "Masculino", "+521234567891"])
    workbook.save(str(xlsx_path))

    inserted, skipped, logs = importer.import_students(str(xlsx_path))
    assert inserted == 1
    assert skipped == 0
    assert logs == []
