import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import queue

from src.config.settings import settings
from src.gui import styles
# from src.gui.dialogs import ValidationDialog # No longer needed
from src.parsers.pdf_parser import PDFParser
from src.storage.excel_db import guardar_guias, get_existing_guides

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Extractor de Guías de Remisión")
        self.geometry("900x600") # Increased size for table
        self.configure(bg=styles.BACKGROUND)
        
        self.queue = queue.Queue()
        self.processing_files = False
        self.parsed_guides = {} # Maps treeview item_id -> Guide object
        
        self._setup_ui()
        self._load_initial_settings()
        self._check_queue()

    def _check_queue(self):
        """Revisa la cola de mensajes del hilo secundario."""
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg.get("type") == "item_processed":
                    self._update_item_status(msg["file_path"], msg["guide"], msg["status"], msg["msg"], msg.get("item_id_ref"))
                elif msg.get("type") == "processing_complete":
                     self.processing_files = False
                     self._update_ui_state()
                elif msg.get("type") == "save_finished":
                     self._save_finished_ui(msg["message"], msg["is_error"])
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_queue)
    
    def _setup_ui(self):
        # Title
        title_frame = tk.Frame(self, bg=styles.BACKGROUND)
        title_frame.pack(fill=tk.X, padx=styles.PADDING_LARGE, pady=(styles.PADDING_LARGE, styles.PADDING_SMALL))
        
        tk.Label(
            title_frame, 
            text="Extractor de Guías de Remisión", 
            font=styles.FONT_TITLE,
            bg=styles.BACKGROUND,
            fg=styles.TEXT_DARK
        ).pack(side=tk.LEFT)

        # Configuration Frame
        config_frame = tk.Frame(self, bg=styles.BACKGROUND)
        config_frame.pack(fill=tk.X, padx=styles.PADDING_LARGE, pady=styles.PADDING_SMALL)

        tk.Label(
            config_frame, 
            text="Excel Destino:", 
            font=styles.FONT_BOLD,
            bg=styles.BACKGROUND,
            fg=styles.TEXT_DARK
        ).pack(side=tk.LEFT)

        self.excel_path_var = tk.StringVar()
        self.excel_path_entry = tk.Entry(
            config_frame, 
            textvariable=self.excel_path_var, 
            readonlybackground=styles.WHITE,
            state="readonly",
            font=styles.FONT_NORMAL,
            bd=1,
            relief="solid",
            width=50
        )
        self.excel_path_entry.pack(side=tk.LEFT, padx=styles.PADDING_SMALL)

        tk.Button(
            config_frame, 
            text="...", 
            command=self.select_excel_path,
            bg=styles.PRIMARY,
            fg=styles.WHITE,
            relief="flat",
            cursor="hand2"
        ).pack(side=tk.LEFT)

        # Toolbar
        toolbar = tk.Frame(self, bg=styles.BACKGROUND)
        toolbar.pack(fill=tk.X, padx=styles.PADDING_LARGE, pady=styles.PADDING_SMALL)
        
        self.add_btn = tk.Button(
            toolbar,
            text="+ Añadir Archivos",
            command=self.select_files,
            bg=styles.PRIMARY,
            fg=styles.WHITE,
            activebackground=styles.PRIMARY_HOVER,
            relief="flat",
            cursor="hand2",
            font=styles.FONT_BOLD
        )
        self.add_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_btn = tk.Button(
            toolbar,
            text="Limpiar Lista",
            command=self.clear_list,
            bg=styles.SECONDARY,
            fg=styles.TEXT_DARK,
            relief="groove",
            cursor="hand2"
        )
        self.clear_btn.pack(side=tk.LEFT)

        # Treeview (Staging Table)
        tree_frame = tk.Frame(self, bg=styles.WHITE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=styles.PADDING_LARGE, pady=styles.PADDING_SMALL)

        columns = ("archivo", "remitente", "transportista", "fecha", "estado")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="extended")
        
        self.tree.heading("archivo", text="Archivo")
        self.tree.heading("remitente", text="Cod. Remitente")
        self.tree.heading("transportista", text="Cod. Transportista")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("estado", text="Estado")
        
        self.tree.column("archivo", width=200)
        self.tree.column("remitente", width=120)
        self.tree.column("transportista", width=120)
        self.tree.column("fecha", width=100)
        self.tree.column("estado", width=150)
        
        # Tags for colors
        self.tree.tag_configure(styles.TAG_VALID, foreground=styles.SUCCESS)
        self.tree.tag_configure(styles.TAG_INVALID, foreground=styles.ERROR)
        self.tree.tag_configure(styles.TAG_DUPLICATE, foreground=styles.WARNING)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Footer Actions
        action_frame = tk.Frame(self, bg=styles.BACKGROUND)
        action_frame.pack(fill=tk.X, padx=styles.PADDING_LARGE, pady=styles.PADDING_LARGE)
        
        self.status_label = tk.Label(
            action_frame, 
            text="Listo.", 
            font=styles.FONT_SMALL,
            bg=styles.BACKGROUND,
            fg=styles.TEXT_LIGHT
        )
        self.status_label.pack(side=tk.LEFT)

        self.process_btn = tk.Button(
            action_frame, 
            text="Guardar Válidos", 
            command=self.save_valid_files,
            bg=styles.SUCCESS,
            fg=styles.WHITE,
            activebackground="#218838",
            activeforeground=styles.WHITE,
            font=styles.FONT_BOLD,
            relief="flat",
            state="disabled",
            cursor="hand2",
            padx=20, pady=5
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
            # Re-validate if items exist?
            if self.tree.get_children():
                self.revalidate_all()

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar PDFs",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if files:
            self.add_files(files)

    def add_files(self, files):
        # Add to tree with "Pending" status
        new_items_to_process = []
        for f in files:
            # Check if file already in tree? For now allow duplicate files logic to handle it or UI to block?
            # Let's verify by filename to avoid adding same file twice to list
            if not self._is_file_in_tree(f):
                item_id = self.tree.insert("", tk.END, values=(Path(f).name, "...", "...", "...", "Pendiente"))
                new_items_to_process.append((item_id, f))
        
        if new_items_to_process:
            self.processing_files = True
            self._update_ui_state()
            threading.Thread(target=self.process_files_thread, args=(new_items_to_process,), daemon=True).start()

    def _is_file_in_tree(self, filepath):
        # This is a simple check, could be improved
        filename = Path(filepath).name
        for item in self.tree.get_children():
            if self.tree.item(item)["values"][0] == filename:
                return True
        return False

    def clear_list(self):
        self.parsed_guides.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._update_ui_state()

    def process_files_thread(self, items):
        excel_path = settings.excel_path
        pdf_parser = PDFParser()
        
        # Load existing guides once for performance if needed, or per item?
        # Better to load once per batch to avoid file I/O lock
        existing_guides = set()
        if excel_path and Path(excel_path).exists():
             try:
                 existing_guides = get_existing_guides(excel_path)
             except Exception:
                 # Handle case where excel might be corrupt or not accessible
                 pass

        for item_id, file_path in items:
            try:
                guides = pdf_parser.extract_guides(file_path)
                
                if not guides:
                    # No guide found or empty
                    self.queue.put({
                        "type": "item_processed", "file_path": file_path, 
                        "guide": None, "status": "no_data", "msg": "No se encontraron datos",
                        "item_id_ref": item_id
                    })
                    continue

                # Assuming 1 guide per file for simplified table row. 
                # If multiple guides, we might need multiple rows or logic.
                # Project seems to assume 1 PDF -> N Guides.
                # If N > 1, maybe we insert multiple rows for same file?
                
                # For now, let's assume one guide per file for simplicity in the UI.
                # If multiple guides are found, we'll just take the first one for display
                # and store all of them.
                
                # If there are multiple guides, we need to update the original placeholder
                # and then insert new rows for subsequent guides from the same file.
                first_guide_processed = False
                for guide in guides:
                     # Validate
                    status = styles.TAG_VALID
                    msg = "Listo para guardar"
                    
                    if guide.cod_remitente == "No encontrado" or guide.cod_transportista == "No encontrado":
                        status = styles.TAG_INVALID
                        msg = "Faltan códigos"
                    else:
                        key = (guide.cod_remitente, guide.cod_transportista)
                        if key in existing_guides:
                            status = styles.TAG_DUPLICATE
                            msg = "Ya existe en Excel"
                    
                    if not first_guide_processed:
                        self.queue.put({
                            "type": "item_processed", 
                            "file_path": file_path, 
                            "guide": guide, 
                            "status": status, 
                            "msg": msg,
                            "item_id_ref": item_id # To update specific row
                        })
                        first_guide_processed = True
                    else:
                        # For subsequent guides from the same file, insert new rows
                        self.queue.put({
                            "type": "item_processed", 
                            "file_path": file_path, 
                            "guide": guide, 
                            "status": status, 
                            "msg": msg,
                            "item_id_ref": None # Indicate new row insertion
                        })
            except Exception as e:
                self.queue.put({
                    "type": "item_processed", "file_path": file_path, 
                    "guide": None, "status": styles.TAG_INVALID, "msg": f"Error: {e}",
                    "item_id_ref": item_id
                })
        
        self.queue.put({"type": "processing_complete"})

    def _update_item_status(self, file_path, guide, status, msg, item_id_ref=None):
        filename = Path(file_path).name
        
        if item_id_ref: # This is an update to an existing placeholder row
           # Update the placeholder
            found_item = item_id_ref
            if guide:
                self.tree.item(found_item, values=(filename, guide.cod_remitente, guide.cod_transportista, guide.fecha, msg), tags=(status,))
                self.parsed_guides[found_item] = guide
            else:
                self.tree.item(found_item, values=(filename, "-", "-", "-", msg), tags=(status,))
                if found_item in self.parsed_guides:
                    del self.parsed_guides[found_item] # Remove if no valid guide
        else: # This is a new guide from a file that already had a guide processed (insert new row)
            vals = (filename, guide.cod_remitente, guide.cod_transportista, guide.fecha, msg) if guide else (filename, "-", "-", "-", msg)
            new_item_id = self.tree.insert("", tk.END, values=vals, tags=(status,))
            if guide:
                self.parsed_guides[new_item_id] = guide
        
        self._update_ui_state()

    def _update_ui_state(self):
        if self.processing_files:
            self.add_btn.config(state="disabled")
            self.clear_btn.config(state="disabled")
            self.process_btn.config(state="disabled")
            self.status_label.config(text="Procesando archivos...")
        else:
            self.add_btn.config(state="normal")
            self.clear_btn.config(state="normal" if self.tree.get_children() else "disabled")
            
            # Enable save button only if there are valid items
            has_valid = False
            for item in self.tree.get_children():
                tags = self.tree.item(item)["tags"]
                if styles.TAG_VALID in tags:
                    has_valid = True
                    break
            
            self.process_btn.config(state="normal" if has_valid else "disabled")
            self.status_label.config(text="Listo.")

    def revalidate_all(self):
        # Re-process all items in the treeview to re-check against new excel path
        # This involves clearing parsed_guides and re-running process_files_thread
        
        # Get all current items and their file paths
        items_to_reprocess = []
        for item_id in self.tree.get_children():
            filename = self.tree.item(item_id)["values"][0]
            # We need the full path, not just filename. This is a limitation of current design.
            # A better approach would be to store the full path in parsed_guides or tree item data.
            # For this iteration, let's just clear and re-add.
            
            # Clear existing items and parsed guides
            self.clear_list() 
            
            # This is a simplified revalidation. A more robust solution would store original file paths
            # and re-process them without user re-selection.
            # For now, we'll just update the status label.
            self.status_label.config(text="Por favor, re-añada los archivos para revalidar con el nuevo Excel.", fg=styles.WARNING)
            return

    def save_valid_files(self):
        excel_path = settings.excel_path
        if not excel_path or not Path(excel_path).exists():
            messagebox.showwarning("Falta configuración", "Por favor seleccione un archivo Excel de destino válido.")
            return

        valid_guides_to_save = []
        for item_id in self.tree.get_children():
            tags = self.tree.item(item_id)["tags"]
            if styles.TAG_VALID in tags and item_id in self.parsed_guides:
                valid_guides_to_save.append(self.parsed_guides[item_id])
        
        if not valid_guides_to_save:
            messagebox.showinfo("Guardar Guías", "No hay guías válidas para guardar.")
            return
        
        self.processing_files = True
        self._update_ui_state()
        threading.Thread(target=self._save_guides_thread, args=(excel_path, valid_guides_to_save), daemon=True).start()

    def _save_guides_thread(self, excel_path, guides):
        try:
            if guides:
                self.queue.put({"type": "save_finished", "message": "Guardando en Excel...", "is_error": False})
                guardar_guias(excel_path, guides)
                self.queue.put({"type": "save_finished", "message": f"Completado! {len(guides)} guías guardadas.", "is_error": False})
            else:
                self.queue.put({"type": "save_finished", "message": "No hay guías nuevas para guardar.", "is_error": False})
        except Exception as e:
            self.queue.put({"type": "save_finished", "message": f"Error guardando: {e}", "is_error": True})

    def _save_finished_ui(self, message, is_error):
        self.processing_files = False
        self._update_ui_state()
        self.status_label.config(text=message, fg=styles.ERROR if is_error else styles.TEXT_LIGHT)
        if not is_error:
            messagebox.showinfo("Proceso Terminado", message)
            # Optionally clear only saved items or all items
            self.clear_list() # Clear all for simplicity after successful save
        else:
            messagebox.showerror("Error", message)
