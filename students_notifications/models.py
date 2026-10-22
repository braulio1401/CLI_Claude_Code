from dataclasses import dataclass


@dataclass(frozen=True)
class Student:
    control: str
    apaterno: str
    amaterno: str
    nombre: str
    email_int: str
    correo_per: str
    sexo: str
    telefono: str

    def as_dict(self) -> dict[str, str]:
        return {
            "control": self.control,
            "apaterno": self.apaterno,
            "amaterno": self.amaterno,
            "nombre": self.nombre,
            "email_int": self.email_int,
            "correo_per": self.correo_per,
            "sexo": self.sexo,
            "telefono": self.telefono,
        }
