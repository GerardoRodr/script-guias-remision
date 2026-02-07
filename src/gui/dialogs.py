import tkinter as tk
from tkinter import ttk
from src.gui import styles

class ValidationDialog(tk.Toplevel):
    def __init__(self, parent, duplicates, invalid_files):
        super().__init__(parent)
        self.title("Validación de Archivos")
        self.geometry("700x500")
        self.configure(bg=styles.BACKGROUND)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        self.duplicates = duplicates
        self.invalid_files = invalid_files
        self.result = False # Default to Cancel
        
        self._setup_ui()
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _setup_ui(self):
        # Header
        header_frame = tk.Frame(self, bg=styles.BACKGROUND)
        header_frame.pack(fill=tk.X, padx=styles.PADDING_LARGE, pady=styles.PADDING_MEDIUM)
        
        total_issues = len(self.duplicates) + len(self.invalid_files)
        
        tk.Label(
            header_frame,
            text=f"¡Se encontraron {total_issues} archivos con observaciones!",
            font=styles.FONT_TITLE,
            bg=styles.BACKGROUND,
            fg=styles.ERROR,
            wraplength=650
        ).pack()
        
        tk.Label(
            header_frame,
            text="Revise los detalles a continuación. Estos archivos NO se guardarán si continúa.",
            font=styles.FONT_NORMAL,
            bg=styles.BACKGROUND,
            fg=styles.TEXT_DARK
        ).pack(pady=(5, 0))

        # Tabs
        tab_control = ttk.Notebook(self)
        
        if self.duplicates:
            self._create_duplicates_tab(tab_control)
            
        if self.invalid_files:
            self._create_invalid_tab(tab_control)
            
        tab_control.pack(expand=1, fill="both", padx=styles.PADDING_LARGE, pady=styles.PADDING_SMALL)

        # Buttons
        btn_frame = tk.Frame(self, bg=styles.BACKGROUND)
        btn_frame.pack(fill=tk.X, padx=styles.PADDING_LARGE, pady=styles.PADDING_LARGE)
        
        tk.Button(
            btn_frame,
            text="Cancelar (No hacer nada)",
            command=self.on_cancel,
            bg=styles.WHITE,
            fg=styles.TEXT_DARK,
            font=styles.FONT_NORMAL,
            relief="groove",
            padx=10
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="Aceptar (Omitir estos y guardar válidos)",
            command=self.on_accept,
            bg=styles.PRIMARY,
            fg=styles.WHITE,
            activebackground=styles.PRIMARY_HOVER,
            activeforeground=styles.WHITE,
            font=styles.FONT_BOLD,
            relief="flat",
            padx=10
        ).pack(side=tk.RIGHT)

    def _create_duplicates_tab(self, tab_control):
        tab = ttk.Frame(tab_control)
        tab_control.add(tab, text=f'Duplicados ({len(self.duplicates)})')
        
        columns = ("remitente", "transportista", "fecha")
        tree = ttk.Treeview(tab, columns=columns, show="headings", selectmode="none")
        
        tree.heading("remitente", text="Guía Remitente")
        tree.heading("transportista", text="Guía Transportista")
        tree.heading("fecha", text="Fecha")
        
        tree.column("remitente", width=150)
        tree.column("transportista", width=150)
        tree.column("fecha", width=100)
        
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        for guia in self.duplicates:
            tree.insert("", tk.END, values=(guia.cod_remitente, guia.cod_transportista, guia.fecha))

    def _create_invalid_tab(self, tab_control):
        tab = ttk.Frame(tab_control)
        tab_control.add(tab, text=f'No Válidos ({len(self.invalid_files)})')
        
        columns = ("archivo", "motivo")
        tree = ttk.Treeview(tab, columns=columns, show="headings", selectmode="none")
        
        tree.heading("archivo", text="Archivo")
        tree.heading("motivo", text="Motivo / Datos Faltantes")
        
        tree.column("archivo", width=200)
        tree.column("motivo", width=400)
        
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        for item in self.invalid_files:
            # item is expected to be a dict or tuple with (filename, reason) or similar
            # For now assuming item is the guide object which has data "No encontrado"
            
            motivo = []
            if item.cod_remitente == "No encontrado": motivo.append("Remitente")
            if item.cod_transportista == "No encontrado": motivo.append("Transportista")
            
            reason_str = f"Falta: {', '.join(motivo)}" if motivo else "Datos incompletos"
            
            # Extract filename from path
            from pathlib import Path
            filename = Path(item.ruta_archivo).name
            
            tree.insert("", tk.END, values=(filename, reason_str))

    def on_accept(self):
        # Confirmation Dialog
        confirm = tk.messagebox.askyesno(
            "Confirmación",
            "Los archivos listados NO se guardarán.\n¿Desea continuar guardando solo los archivos válidos?",
            parent=self
        )
        if confirm:
            self.result = True
            self.destroy()

    def on_cancel(self):
        self.result = False
        self.destroy()
