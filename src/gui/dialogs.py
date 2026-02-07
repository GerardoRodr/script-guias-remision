import tkinter as tk
from tkinter import ttk
from src.gui import styles

class DuplicateDialog(tk.Toplevel):
    def __init__(self, parent, duplicates):
        super().__init__(parent)
        self.title("Guías Duplicadas Detectadas")
        self.geometry("600x400")
        self.configure(bg=styles.BACKGROUND)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        self.duplicates = duplicates
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
        
        tk.Label(
            header_frame,
            text=f"¡Se encontraron {len(self.duplicates)} guías que ya existen!",
            font=styles.FONT_TITLE,
            bg=styles.BACKGROUND,
            fg=styles.ERROR,
            wraplength=550
        ).pack()
        
        tk.Label(
            header_frame,
            text="Las siguientes guías ya están registradas en el Excel:",
            font=styles.FONT_NORMAL,
            bg=styles.BACKGROUND,
            fg=styles.TEXT_DARK
        ).pack(pady=(5, 0))

        # List Area (Treeview)
        list_frame = tk.Frame(self, bg=styles.WHITE)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=styles.PADDING_LARGE, pady=styles.PADDING_SMALL)
        
        columns = ("remitente", "transportista", "fecha")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="none")
        
        self.tree.heading("remitente", text="Guía Remitente")
        self.tree.heading("transportista", text="Guía Transportista")
        self.tree.heading("fecha", text="Fecha")
        
        self.tree.column("remitente", width=150)
        self.tree.column("transportista", width=150)
        self.tree.column("fecha", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate data
        for guia in self.duplicates:
            self.tree.insert("", tk.END, values=(guia.cod_remitente, guia.cod_transportista, guia.fecha))

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
            text="Aceptar (Ignorar duplicados y continuar)",
            command=self.on_accept,
            bg=styles.PRIMARY,
            fg=styles.WHITE,
            activebackground=styles.PRIMARY_HOVER,
            activeforeground=styles.WHITE,
            font=styles.FONT_BOLD,
            relief="flat",
            padx=10
        ).pack(side=tk.RIGHT)

    def on_accept(self):
        # Confirmation Dialog
        confirm = tk.messagebox.askyesno(
            "Confirmación",
            "Solo se procesarán las guías que NO están en la lista.\n¿Desea continuar?",
            parent=self
        )
        if confirm:
            self.result = True
            self.destroy()

    def on_cancel(self):
        self.result = False
        self.destroy()
