import mimetypes
import smtplib
from collections.abc import Iterable
from email.message import EmailMessage
from pathlib import Path

from .models import Student


def _normalize_extension(extension: str) -> str:
    extension_text = extension.strip().lower()
    if not extension_text:
        return ""
    return extension_text if extension_text.startswith(".") else f".{extension_text}"


def _attach_file(message: EmailMessage, path: Path) -> None:
    content_type, _ = mimetypes.guess_type(path.name)
    if content_type is None:
        content_type = "application/octet-stream"
    main_type, sub_type = content_type.split("/", 1)
    with path.open("rb") as attachment_file:
        message.add_attachment(
            attachment_file.read(),
            maintype=main_type,
            subtype=sub_type,
            filename=path.name,
        )


def send_email_notifications(
    subject: str,
    body: str,
    students: Iterable[Student],
    attachments_folder: str,
    extension: str,
    config: dict[str, str],
) -> list[str]:
    smtp_server = config.get("smtp_server", "smtp.office365.com")
    smtp_port = int(config.get("smtp_port", "587"))
    email_address = config.get("email_address", "")
    email_password = config.get("email_password", "")
    path_folder = Path(attachments_folder.strip()) if attachments_folder else None
    extension = _normalize_extension(extension)
    errors: list[str] = []

    if not email_address or not email_password:
        raise ValueError("Configuración de correo incompleta")

    with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(email_address, email_password)

        for student in students:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = email_address
            message["To"] = student.email_int
            message["Cc"] = student.correo_per
            message.set_content(body)

            if path_folder and extension:
                candidate = path_folder / f"{student.control}{extension}"
                if candidate.exists():
                    _attach_file(message, candidate)
                else:
                    errors.append(f"Adjunto no encontrado para {student.control}: {candidate}")

            recipients = [student.email_int, student.correo_per]
            try:
                smtp.send_message(message, from_addr=email_address, to_addrs=recipients)
            except Exception as exc:
                errors.append(f"Error envío correo {student.control}: {exc}")

    return errors
