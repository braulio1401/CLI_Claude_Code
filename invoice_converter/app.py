import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .converter import convert_xml_to_pdf, merge_pdfs


class InvoiceConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Factura PDF/XML Converter")
        self.geometry("850x520")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.pdf_path = tk.StringVar()
        self.xml_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.folder_name = tk.StringVar(value="factura_combinada")

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self)
        frame.grid(sticky="nsew", padx=12, pady=12)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Factura PDF original:").grid(row=0, column=0, sticky="w", pady=4)
        pdf_entry = ttk.Entry(frame, textvariable=self.pdf_path)
        pdf_entry.grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(frame, text="Seleccionar PDF", command=self.select_pdf).grid(row=0, column=2, padx=4)

        ttk.Label(frame, text="Factura XML:").grid(row=1, column=0, sticky="w", pady=4)
        xml_entry = ttk.Entry(frame, textvariable=self.xml_path)
        xml_entry.grid(row=1, column=1, sticky="ew", padx=4)
        ttk.Button(frame, text="Seleccionar XML", command=self.select_xml).grid(row=1, column=2, padx=4)

        ttk.Label(frame, text="Carpeta de salida:").grid(row=2, column=0, sticky="w", pady=4)
        output_entry = ttk.Entry(frame, textvariable=self.output_folder)
        output_entry.grid(row=2, column=1, sticky="ew", padx=4)
        ttk.Button(frame, text="Seleccionar carpeta", command=self.select_output_folder).grid(row=2, column=2, padx=4)

        ttk.Label(frame, text="Nombre de carpeta nueva:").grid(row=3, column=0, sticky="w", pady=4)
        folder_name_entry = ttk.Entry(frame, textvariable=self.folder_name)
        folder_name_entry.grid(row=3, column=1, sticky="ew", padx=4, pady=4)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=12, sticky="ew")
        button_frame.columnconfigure((0, 1), weight=1)
        tk.Button(
            button_frame,
            text="Convertir y Combinar",
            command=self.convert_and_merge,
            bg="#007bff",
            fg="white",
            activebackground="#0056b3",
            relief="raised",
        ).grid(row=0, column=0, sticky="ew", padx=4)
        tk.Button(
            button_frame,
            text="Limpiar campos",
            command=self.clear_fields,
            bg="#6c757d",
            fg="white",
            activebackground="#5a6268",
            relief="raised",
        ).grid(row=0, column=1, sticky="ew", padx=4)

        ttk.Label(frame, text="Registro de eventos:").grid(row=5, column=0, sticky="w", pady=4)
        self.log_text = tk.Text(frame, height=12, state="disabled", wrap="word")
        self.log_text.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=4)
        frame.rowconfigure(6, weight=1)

    def _append_log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def select_pdf(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")], title="Seleccionar factura PDF")
        if path:
            self.pdf_path.set(path)

    def select_xml(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")], title="Seleccionar factura XML")
        if path:
            self.xml_path.set(path)

    def select_output_folder(self) -> None:
        path = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if path:
            self.output_folder.set(path)

    def clear_fields(self) -> None:
        self.pdf_path.set("")
        self.xml_path.set("")
        self.output_folder.set("")
        self.folder_name.set("factura_combinada")
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")

    def convert_and_merge(self) -> None:
        pdf_file = self.pdf_path.get().strip()
        xml_file = self.xml_path.get().strip()
        output_folder = self.output_folder.get().strip()
        folder_name = self.folder_name.get().strip() or "factura_combinada"

        if not pdf_file or not xml_file or not output_folder:
            messagebox.showwarning("Campos incompletos", "Seleccione el PDF, el XML y la carpeta de salida.")
            return

        if not Path(pdf_file).is_file():
            messagebox.showerror("Error", "El archivo PDF seleccionado no existe.")
            return
        if not Path(xml_file).is_file():
            messagebox.showerror("Error", "El archivo XML seleccionado no existe.")
            return

        destination_dir = Path(output_folder) / folder_name
        destination_dir.mkdir(parents=True, exist_ok=True)
        xml_pdf = destination_dir / f"{Path(xml_file).stem}_xml_convertido.pdf"
        merged_pdf = destination_dir / f"{Path(pdf_file).stem}_combinado.pdf"

        try:
            self._append_log("Convirtiendo XML a PDF...")
            convert_xml_to_pdf(xml_file, str(xml_pdf), title=Path(xml_file).stem)
            self._append_log(f"PDF generado: {xml_pdf}")

            self._append_log("Combinando PDF original y PDF generado...")
            merge_pdfs([pdf_file, str(xml_pdf)], str(merged_pdf))
            self._append_log(f"PDF combinado generado: {merged_pdf}")

            messagebox.showinfo("Listo", f"El PDF combinado se creó en:\n{merged_pdf}")
        except Exception as exc:
            self._append_log(f"Error: {exc}")
            messagebox.showerror("Error", f"No se pudo generar el PDF combinado.\n{exc}")


def main() -> None:
    app = InvoiceConverterApp()
    app.mainloop()
