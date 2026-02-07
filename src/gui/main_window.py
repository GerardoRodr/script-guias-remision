import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import queue

from src.config.settings import settings
from src.gui import styles
from src.gui.dialogs import ValidationDialog
from src.parsers.pdf_parser import PDFParser
from src.storage.excel_db import guardar_guias, get_existing_guides

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Extractor de Guías de Remisión")
        self.geometry("600x500")
        self.configure(bg=styles.BACKGROUND)
        self.resizable(False, False)

        self.files_to_process = []
        self.queue = queue.Queue()
        
        self._setup_ui()
        self._load_initial_settings()
        self._check_queue()

    def _check_queue(self):
        """Revisa la cola de mensajes del hilo secundario."""
        try:
            msg = self.queue.get_nowait()
            if isinstance(msg, dict) and msg.get("type") == "validation":
                self._show_validation_dialog(msg["duplicates"], msg["invalid"], msg["valid"], msg["excel_path"])
            elif isinstance(msg, dict) and msg.get("type") == "finished":
                 self._process_finished_ui(msg["message"], msg["is_error"])
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_queue)
    
    def _show_validation_dialog(self, duplicates, invalid, valid, excel_path):
        """Muestra el diálogo de validación en el hilo principal."""
        dialog = ValidationDialog(self, duplicates, invalid)
        self.wait_window(dialog)
        
        if dialog.result:
            # Si el usuario aceptó, continuamos guardando SOLO los válidos
            if valid:
                threading.Thread(target=self.save_guides_thread, args=(excel_path, valid), daemon=True).start()
            else:
                 self.process_finished("No hay guías válidas para guardar.", is_error=False)
        else:
            # Cancelado
            self.process_finished("Operación cancelada por el usuario.", is_error=False)

    def _setup_ui(self):
        # Title
        title_label = tk.Label(
            self, 
            text="Extractor de Guías de Remisión", 
            font=styles.FONT_TITLE,
            bg=styles.BACKGROUND,
            fg=styles.TEXT_DARK
        )
        title_label.pack(pady=styles.PADDING_LARGE)

        # Configuration Frame
        config_frame = tk.Frame(self, bg=styles.BACKGROUND)
        config_frame.pack(fill=tk.X, padx=styles.PADDING_LARGE, pady=styles.PADDING_SMALL)

        tk.Label(
            config_frame, 
            text="Archivo Destino (Excel):", 
            font=styles.FONT_BOLD,
            bg=styles.BACKGROUND,
            fg=styles.TEXT_DARK
        ).pack(anchor="w")

        self.excel_path_var = tk.StringVar()
        self.excel_path_entry = tk.Entry(
            config_frame, 
            textvariable=self.excel_path_var, 
            readonlybackground=styles.WHITE,
            state="readonly",
            font=styles.FONT_NORMAL,
            bd=1,
            relief="solid"
        )
        self.excel_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, styles.PADDING_SMALL))

        tk.Button(
            config_frame, 
            text="...", 
            command=self.select_excel_path,
            bg=styles.PRIMARY,
            fg=styles.WHITE,
            activebackground=styles.PRIMARY_HOVER,
            activeforeground=styles.WHITE,
            relief="flat",
            cursor="hand2"
        ).pack(side=tk.RIGHT)

        # Selection Area
        self.dnd_frame = tk.Frame(
            self, 
            bg=styles.WHITE, 
            bd=2, 
            relief="groove"
        )
        self.dnd_frame.pack(
            fill=tk.BOTH, 
            expand=True, 
            padx=styles.PADDING_LARGE, 
            pady=styles.PADDING_LARGE
        )

        # Container for centering
        center_frame = tk.Frame(self.dnd_frame, bg=styles.WHITE)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.dnd_label = tk.Label(
            center_frame,
            text="Haz clic para seleccionar archivos PDF",
            font=styles.FONT_NORMAL,
            bg=styles.WHITE,
            fg=styles.TEXT_LIGHT,
            justify=tk.CENTER,
            cursor="hand2"
        )
        self.dnd_label.pack(pady=(0, 10))

        self.select_btn = tk.Button(
            center_frame,
            text="Seleccionar Archivos",
            command=self.select_files,
            bg=styles.PRIMARY,
            fg=styles.WHITE,
            activebackground=styles.PRIMARY_HOVER,
            relief="flat",
            cursor="hand2"
        )
        self.select_btn.pack()

        # Bind events
        self.dnd_frame.bind("<Button-1>", lambda e: self.select_files())
        self.dnd_label.bind("<Button-1>", lambda e: self.select_files())

        # Status and Actions
        action_frame = tk.Frame(self, bg=styles.BACKGROUND)
        action_frame.pack(fill=tk.X, padx=styles.PADDING_LARGE, pady=styles.PADDING_LARGE)

        self.status_label = tk.Label(
            action_frame, 
            text="Esperando selección...", 
            font=styles.FONT_SMALL,
            bg=styles.BACKGROUND,
            fg=styles.TEXT_LIGHT
        )
        self.status_label.pack(side=tk.LEFT)

        self.process_btn = tk.Button(
            action_frame, 
            text="Procesar Archivos", 
            command=self.start_processing,
            bg=styles.SUCCESS,
            fg=styles.WHITE,
            activebackground="#218838", # Darker green
            activeforeground=styles.WHITE,
            font=styles.FONT_BOLD,
            relief="flat",
            state="disabled",
            cursor="hand2"
        )
        self.process_btn.pack(side=tk.RIGHT)

    def _load_initial_settings(self):
        path = settings.excel_path
        if path:
            self.excel_path_var.set(path)
        else:
            self.excel_path_var.set("Seleccione un archivo...")

    def select_excel_path(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if path:
            settings.excel_path = path
            self.excel_path_var.set(path)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar PDFs",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if files:
            self.add_files(files)

    def add_files(self, files):
        new_files = [f for f in files if f not in self.files_to_process]
        if not new_files:
            return

        self.files_to_process.extend(new_files)
        self.update_status(f"{len(self.files_to_process)} archivos seleccionados")
        self.update_dnd_label()
        self.process_btn.config(state="normal")

    def update_dnd_label(self):
        if not self.files_to_process:
            self.dnd_label.config(text="Haz clic aquí para seleccionar archivos PDF")
        else:
            files_text = "\n".join([Path(f).name for f in self.files_to_process[:5]])
            if len(self.files_to_process) > 5:
                files_text += f"\n... y {len(self.files_to_process) - 5} más"
            self.dnd_label.config(text=f"Archivos listos:\n{files_text}")

    def update_status(self, text, is_error=False):
        color = styles.ERROR if is_error else styles.TEXT_LIGHT
        self.status_label.config(text=text, fg=color)
        self.update_idletasks()

    def start_processing(self):
        excel_path = settings.excel_path
        if not excel_path or not Path(excel_path).exists():
            messagebox.showwarning("Falta configuración", "Por favor seleccione un archivo Excel de destino válido.")
            return

        self.process_btn.config(state="disabled")
        self.update_status("Procesando...")
        
        # Run in thread to keep UI responsive
        threading.Thread(target=self.process_logic, daemon=True).start()

    def process_logic(self):
        excel_path = settings.excel_path
        pdf_parser = PDFParser()
        all_guides = []
        errors = []

        try:
            # 1. Extraer Guías
            for pdf_path in self.files_to_process:
                self.update_status(f"Leyendo: {Path(pdf_path).name}")
                try:
                    guides = pdf_parser.extract_guides(pdf_path)
                    all_guides.extend(guides)
                except Exception as e:
                    errors.append(f"{Path(pdf_path).name}: {str(e)}")

            if not all_guides:
                self.process_finished(f"No se encontraron guías. {len(errors)} errores.", is_error=True)
                return
            
            # 2. Verificar Validez y Duplicados
            existing_guides = get_existing_guides(excel_path)
            
            duplicates = []
            invalid = []
            valid = []
            
            for guide in all_guides:
                # Criterio de invalidez: no se encontró remitente o transportista
                if guide.cod_remitente == "No encontrado" and guide.cod_transportista == "No encontrado":
                    invalid.append(guide)
                    continue

                if guide.cod_remitente == "No encontrado" or guide.cod_transportista == "No encontrado":
                     # Podríamos ser más estrictos, pero según el parser actual, si falta uno de los dos códigos
                     # podría considerarse inválida o incompleta. El usuario pidió "ni de remitente ni de transportista",
                     # pero para seguridad, si falta CUALQUIERA de los dos códigos principales, lo marco inválido.
                     invalid.append(guide)
                     continue

                key = (guide.cod_remitente, guide.cod_transportista)
                if key in existing_guides:
                    duplicates.append(guide)
                else:
                    valid.append(guide)
            
            if duplicates or invalid:
                # Enviar a la UI para mostrar diálogo
                self.queue.put({
                    "type": "validation", 
                    "duplicates": duplicates,
                    "invalid": invalid,
                    "valid": valid,
                    "excel_path": excel_path
                })
            else:
                # Si todo está perfecto, guardamos directo
                self.save_guides_thread(excel_path, valid)

        except Exception as e:
            self.process_finished(f"Error crítico: {str(e)}", is_error=True)

    def save_guides_thread(self, excel_path, guides):
        try:
            if guides:
                self.update_status("Guardando en Excel...")
                guardar_guias(excel_path, guides)
                self.process_finished(f"Completado! {len(guides)} guías guardadas.")
            else:
                self.process_finished("No hay guías nuevas para guardar.")
        except Exception as e:
            self.process_finished(f"Error guardando: {e}", is_error=True)

    def process_finished(self, message, is_error=False):
        self.queue.put({"type": "finished", "message": message, "is_error": is_error})

    def _process_finished_ui(self, message, is_error):
        self.update_status(message, is_error)
        self.process_btn.config(state="normal")
        if not is_error:
            messagebox.showinfo("Proceso Terminado", message)
            self.files_to_process = []
            self.update_dnd_label()
        else:
            messagebox.showerror("Error", message)
