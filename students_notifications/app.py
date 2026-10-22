import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .db import (
    delete_student,
    get_all_config,
    init_db,
    list_students,
    save_config,
    upsert_student,
)
from .email_sender import send_email_notifications
from .importer import import_students
from .models import Student
from .validators import (
    normalize_email,
    normalize_name,
    normalize_sexo,
    validate_email,
    validate_phone,
)
from .whatsapp_sender import send_whatsapp_notifications


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Administración de Notificaciones")
        self.geometry("1100x750")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        init_db()
        self.selected_controls: dict[str, bool] = {}
        self.attachment_folder: str = ""
        self.selected_extension = tk.StringVar(value=".pdf")
        self.whatsapp_enabled = tk.BooleanVar(value=False)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(sticky="nsew", padx=10, pady=10)

        self._build_students_tab()
        self._build_notifications_tab()
        self._build_import_tab()
        self._build_config_tab()

        self.load_students()
        self._load_config_values()

    def _build_students_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(9, weight=1)
        self.notebook.add(frame, text="Estudiantes")

        labels = [
            ("Control", 0),
            ("Apellido paterno", 1),
            ("Apellido materno", 2),
            ("Nombre", 3),
            ("Email institucional", 4),
            ("Correo personal", 5),
            ("Sexo", 6),
            ("Teléfono", 7),
        ]
        self.student_entries: dict[str, tk.Entry] = {}
        for label_text, row in labels:
            label = ttk.Label(frame, text=label_text)
            label.grid(row=row, column=0, sticky="w", pady=4, padx=4)
            entry = ttk.Entry(frame)
            entry.grid(row=row, column=1, sticky="ew", pady=4, padx=4)
            self.student_entries[label_text] = entry

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10, sticky="ew")
        button_frame.columnconfigure((0, 1, 2, 3), weight=1)

        tk.Button(
            button_frame,
            text="Guardar/Actualizar",
            command=self.save_student,
            bg="#28a745",
            fg="white",
            activebackground="#218838",
            relief="raised",
        ).grid(row=0, column=0, sticky="ew", padx=2)
        tk.Button(
            button_frame,
            text="Eliminar",
            command=self.delete_student_action,
            bg="#dc3545",
            fg="white",
            activebackground="#c82333",
            relief="raised",
        ).grid(row=0, column=1, sticky="ew", padx=2)
        tk.Button(
            button_frame,
            text="Limpiar",
            command=self.clear_student_form,
            bg="#6c757d",
            fg="white",
            activebackground="#5a6268",
            relief="raised",
        ).grid(row=0, column=2, sticky="ew", padx=2)
        tk.Button(
            button_frame,
            text="Buscar por control",
            command=self.search_student,
            bg="#007bff",
            fg="white",
            activebackground="#0069d9",
            relief="raised",
        ).grid(row=0, column=3, sticky="ew", padx=2)

        columns = ("control", "apaterno", "amaterno", "nombre", "email_int", "correo_per", "sexo", "telefono")
        self.student_tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.student_tree.heading(col, text=col.capitalize())
            self.student_tree.column(col, width=120, anchor="w")
        self.student_tree.grid(row=9, column=0, columnspan=2, sticky="nsew", pady=8, padx=4)
        self.student_tree.bind("<Double-1>", self._on_student_row_double_click)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=9, column=2, sticky="ns")

    def _build_notifications_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(1, weight=1)
        self.notebook.add(frame, text="Notificaciones")

        ttk.Label(frame, text="Nombre destinatario:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.recipient_name_entry = ttk.Entry(frame)
        self.recipient_name_entry.grid(row=0, column=1, columnspan=3, sticky="ew", padx=4, pady=4)

        ttk.Label(frame, text="Asunto:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.subject_entry = ttk.Entry(frame)
        self.subject_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=4, pady=4)

        ttk.Label(frame, text="Mensaje:").grid(row=2, column=0, sticky="nw", padx=4, pady=4)
        self.message_text = tk.Text(frame, height=10, wrap="word")
        self.message_text.grid(row=2, column=1, columnspan=3, sticky="nsew", padx=4, pady=4)

        frame.rowconfigure(2, weight=1)

        self.send_whatsapp_checkbox = ttk.Checkbutton(
            frame,
            text="Notificar por WhatsApp",
            variable=self.whatsapp_enabled,
        )
        self.send_whatsapp_checkbox.grid(row=3, column=0, sticky="w", padx=4, pady=4)

        ttk.Button(frame, text="Seleccionar carpeta de adjuntos", command=self.browse_attachment_folder).grid(
            row=2, column=1, sticky="ew", padx=4, pady=4
        )
        ttk.Label(frame, text="Extensión de adjunto:").grid(row=2, column=2, sticky="e", padx=4, pady=4)
        self.extension_combo = ttk.Combobox(
            frame,
            textvariable=self.selected_extension,
            values=[".pdf", ".docx", ".xlsx", ".jpg", ".png"],
            state="readonly",
        )
        self.extension_combo.grid(row=2, column=3, sticky="w", padx=4, pady=4)

        selection_frame = ttk.Frame(frame)
        selection_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=6, padx=4)
        selection_frame.columnconfigure((0, 1, 2), weight=1)
        tk.Button(
            selection_frame,
            text="Marcar todos",
            command=self.select_all,
            bg="#17a2b8",
            fg="white",
            activebackground="#117a8b",
            relief="raised",
        ).grid(row=0, column=0, sticky="ew", padx=2)
        tk.Button(
            selection_frame,
            text="Desmarcar todos",
            command=self.deselect_all,
            bg="#ffc107",
            fg="black",
            activebackground="#e0a800",
            relief="raised",
        ).grid(row=0, column=1, sticky="ew", padx=2)
        tk.Button(
            selection_frame,
            text="Enviar notificación",
            command=self.send_notifications,
            bg="#007bff",
            fg="white",
            activebackground="#0069d9",
            relief="raised",
        ).grid(row=0, column=2, sticky="ew", padx=2)

        self.notification_tree = ttk.Treeview(
            frame,
            columns=("selected", "control", "nombre", "email_int", "correo_per", "telefono"),
            show="headings",
            selectmode="none",
        )
        self.notification_tree.heading("selected", text="Seleccionado")
        self.notification_tree.heading("control", text="Control")
        self.notification_tree.heading("nombre", text="Nombre")
        self.notification_tree.heading("email_int", text="Email institucional")
        self.notification_tree.heading("correo_per", text="Correo personal")
        self.notification_tree.heading("telefono", text="Teléfono")
        self.notification_tree.column("selected", width=100, anchor="center")
        self.notification_tree.column("control", width=100)
        self.notification_tree.column("nombre", width=180)
        self.notification_tree.column("email_int", width=180)
        self.notification_tree.column("correo_per", width=180)
        self.notification_tree.column("telefono", width=120)
        self.notification_tree.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=4, pady=4)
        self.notification_tree.bind("<Button-1>", self._toggle_notification_selection)

        self.notification_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.notification_tree.yview)
        self.notification_tree.configure(yscroll=self.notification_scrollbar.set)
        self.notification_scrollbar.grid(row=5, column=4, sticky="ns")

    def _build_import_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(1, weight=1)
        self.notebook.add(frame, text="Carga masiva")

        ttk.Label(frame, text="Archivo CSV/XLSX:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.import_path_entry = ttk.Entry(frame)
        self.import_path_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        ttk.Button(frame, text="Seleccionar archivo", command=self.browse_import_file).grid(
            row=0, column=2, sticky="ew", padx=4, pady=4
        )
        ttk.Button(frame, text="Importar", command=self.import_students_action).grid(
            row=0, column=3, sticky="ew", padx=4, pady=4
        )

        self.log_text = tk.Text(frame, height=18, state="disabled", wrap="word")
        self.log_text.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=4, pady=4)
        log_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscroll=log_scroll.set)
        log_scroll.grid(row=1, column=4, sticky="ns")
        frame.rowconfigure(1, weight=1)

    def _build_config_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(1, weight=1)
        self.notebook.add(frame, text="Configuración")

        config_items = [
            ("Servidor SMTP", "smtp_server"),
            ("Puerto SMTP", "smtp_port"),
            ("Correo Office365", "email_address"),
            ("Contraseña de correo", "email_password"),
            ("Teléfono WhatsApp", "whatsapp_phone"),
        ]
        self.config_entries: dict[str, tk.Entry] = {}
        for index, (label_text, key) in enumerate(config_items):
            ttk.Label(frame, text=label_text).grid(row=index, column=0, sticky="w", padx=4, pady=4)
            entry = ttk.Entry(frame, show="*" if key == "email_password" else "")
            entry.grid(row=index, column=1, sticky="ew", padx=4, pady=4)
            self.config_entries[key] = entry

        ttk.Button(frame, text="Guardar configuración", command=self.save_config_values).grid(
            row=len(config_items), column=0, columnspan=2, sticky="ew", padx=4, pady=10
        )

    def _load_config_values(self) -> None:
        config = get_all_config()
        defaults = {
            "smtp_server": "smtp.office365.com",
            "smtp_port": "587",
            "email_address": "",
            "email_password": "",
            "whatsapp_phone": "",
        }
        for key, entry in self.config_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, config.get(key, defaults[key]))

    def save_config_values(self) -> None:
        for key, entry in self.config_entries.items():
            save_config(key, entry.get())
        messagebox.showinfo("Configuración", "Configuración guardada correctamente.")

    def save_student(self) -> None:
        data = {
            "control": self.student_entries["Control"].get().strip(),
            "apaterno": normalize_name(self.student_entries["Apellido paterno"].get()),
            "amaterno": normalize_name(self.student_entries["Apellido materno"].get()),
            "nombre": normalize_name(self.student_entries["Nombre"].get()),
            "email_int": normalize_email(self.student_entries["Email institucional"].get()),
            "correo_per": normalize_email(self.student_entries["Correo personal"].get()),
            "sexo": normalize_sexo(self.student_entries["Sexo"].get()),
            "telefono": self.student_entries["Teléfono"].get().strip().replace(" ", "").replace("-", ""),
        }
        if not data["control"]:
            messagebox.showwarning("Datos incompletos", "El número de control es obligatorio.")
            return
        if not validate_email(data["email_int"]):
            messagebox.showwarning("Email inválido", "El email institucional no es válido.")
            return
        if not validate_email(data["correo_per"]):
            messagebox.showwarning("Email inválido", "El correo personal no es válido.")
            return
        if not validate_phone(data["telefono"]):
            messagebox.showwarning("Teléfono inválido", "El teléfono no es válido.")
            return

        student = Student(**data)
        upsert_student(student)
        messagebox.showinfo("Estudiante", "Datos del estudiante guardados correctamente.")
        self.load_students()
        self.clear_student_form()

    def delete_student_action(self) -> None:
        control = self.student_entries["Control"].get().strip()
        if not control:
            messagebox.showwarning("Eliminar", "Ingrese el número de control a eliminar.")
            return
        if messagebox.askyesno("Eliminar", f"¿Eliminar estudiante {control}?"):
            delete_student(control)
            self.load_students()
            self.clear_student_form()

    def search_student(self) -> None:
        control = self.student_entries["Control"].get().strip()
        if not control:
            messagebox.showwarning("Buscar", "Ingrese número de control para buscar.")
            return
        student = list(filter(lambda item: item.control == control, list_students()))
        if not student:
            messagebox.showinfo("Buscar", "No se encontró el estudiante.")
            return
        self._fill_student_form(student[0])

    def clear_student_form(self) -> None:
        for entry in self.student_entries.values():
            entry.delete(0, tk.END)

    def _fill_student_form(self, student: Student) -> None:
        self.student_entries["Control"].delete(0, tk.END)
        self.student_entries["Control"].insert(0, student.control)
        self.student_entries["Apellido paterno"].delete(0, tk.END)
        self.student_entries["Apellido paterno"].insert(0, student.apaterno)
        self.student_entries["Apellido materno"].delete(0, tk.END)
        self.student_entries["Apellido materno"].insert(0, student.amaterno)
        self.student_entries["Nombre"].delete(0, tk.END)
        self.student_entries["Nombre"].insert(0, student.nombre)
        self.student_entries["Email institucional"].delete(0, tk.END)
        self.student_entries["Email institucional"].insert(0, student.email_int)
        self.student_entries["Correo personal"].delete(0, tk.END)
        self.student_entries["Correo personal"].insert(0, student.correo_per)
        self.student_entries["Sexo"].delete(0, tk.END)
        self.student_entries["Sexo"].insert(0, student.sexo)
        self.student_entries["Teléfono"].delete(0, tk.END)
        self.student_entries["Teléfono"].insert(0, student.telefono)

    def load_students(self) -> None:
        for child in self.student_tree.get_children():
            self.student_tree.delete(child)
        for child in self.notification_tree.get_children():
            self.notification_tree.delete(child)
        self.selected_controls.clear()

        students = list_students()
        for student in students:
            self.student_tree.insert(
                "",
                "end",
                iid=student.control,
                values=(
                    student.control,
                    student.apaterno,
                    student.amaterno,
                    student.nombre,
                    student.email_int,
                    student.correo_per,
                    student.sexo,
                    student.telefono,
                ),
            )
            self.notification_tree.insert(
                "",
                "end",
                iid=student.control,
                values=("☐", student.control, student.nombre, student.email_int, student.correo_per, student.telefono),
            )
            self.selected_controls[student.control] = False

    def _on_student_row_double_click(self, event: tk.Event[tk.Widget]) -> None:
        selected = self.student_tree.selection()
        if not selected:
            return
        student = list_students()
        found = next((s for s in student if s.control == selected[0]), None)
        if found:
            self._fill_student_form(found)

    def _toggle_notification_selection(self, event: tk.Event[tk.Widget]) -> None:
        item = self.notification_tree.identify_row(event.y)
        if not item:
            return
        if self.notification_tree.identify_column(event.x) != "#1":
            return
        current = self.selected_controls.get(item, False)
        self.selected_controls[item] = not current
        self.notification_tree.set(item, "selected", "☑" if not current else "☐")

    def select_all(self) -> None:
        for control in self.selected_controls:
            self.selected_controls[control] = True
            self.notification_tree.set(control, "selected", "☑")

    def deselect_all(self) -> None:
        for control in self.selected_controls:
            self.selected_controls[control] = False
            self.notification_tree.set(control, "selected", "☐")

    def browse_attachment_folder(self) -> None:
        folder = filedialog.askdirectory(title="Seleccionar carpeta de adjuntos")
        if folder:
            self.attachment_folder = folder
            messagebox.showinfo("Adjuntos", f"Carpeta de adjuntos seleccionada: {folder}")

    def browse_import_file(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx;*.xls")],
            title="Seleccionar archivo de importación",
        )
        if path:
            self.import_path_entry.delete(0, tk.END)
            self.import_path_entry.insert(0, path)

    def import_students_action(self) -> None:
        path = self.import_path_entry.get().strip()
        if not path:
            messagebox.showwarning("Importar", "Seleccione un archivo de importación.")
            return
        try:
            inserted, skipped, logs = import_students(path)
            self._append_log(f"Importados: {inserted}, Saltados: {skipped}")
            for entry in logs:
                self._append_log(entry)
            self.load_students()
        except Exception as exc:
            messagebox.showerror("Importar", str(exc))

    def _append_log(self, text: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{text}\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def _get_selected_students(self) -> list[Student]:
        all_students = list_students()
        return [student for student in all_students if self.selected_controls.get(student.control)]

    def send_notifications(self) -> None:
        students = self._get_selected_students()
        if not students:
            messagebox.showwarning("Enviar", "Seleccione al menos un estudiante para notificar.")
            return
        subject = self.subject_entry.get().strip()
        recipient_name = self.recipient_name_entry.get().strip()
        body = self.message_text.get("1.0", tk.END).strip()
        if not subject or not body:
            messagebox.showwarning("Enviar", "Asunto y mensaje son obligatorios.")
            return
        if recipient_name:
            body = f"Estimado/a {recipient_name},\n\n{body}"
        config = get_all_config()
        email_errors: list[str] = []
        whatsapp_errors: list[str] = []
        try:
            email_errors = send_email_notifications(
                subject,
                body,
                students,
                self.attachment_folder,
                self.selected_extension.get(),
                config,
            )
        except Exception as exc:
            email_errors.append(str(exc))

        if self.whatsapp_enabled.get():
            recipients = [student.telefono for student in students]
            whatsapp_errors = send_whatsapp_notifications(recipients, body)

        report = []
        if email_errors:
            report.append("Errores email:")
            report.extend(email_errors)
        if whatsapp_errors:
            report.append("Errores WhatsApp:")
            report.extend(whatsapp_errors)
        if report:
            self._append_log("\n".join(report))
            messagebox.showwarning("Notificación", "Proceso completado con advertencias. Revise el log.")
        else:
            messagebox.showinfo("Notificación", "Notificaciones enviadas correctamente.")


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
