import threading
from tkinter import filedialog, messagebox, VERTICAL
import customtkinter as ctk
from gestor_archivos import GestorArchivosLogic

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GestorArchivosGUI:
    def __init__(self):
        self.logic = GestorArchivosLogic(log_callback=self.log, update_ui_callback=self.update_ui)
        
        self.root = ctk.CTk()
        self.root.title("Gestor de Archivos - Copia sin Duplicados")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.ruta_origen = ctk.StringVar()
        self.ruta_destino = ctk.StringVar()
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True)
        
        canvas = ctk.CTkCanvas(container, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(container, orientation=VERTICAL, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.main_frame = ctk.CTkFrame(canvas)
        self.canvas_window = canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.main_frame.bind("<Configure>", on_frame_configure)
        
        def on_canvas_resize(event):
            canvas.itemconfig(self.canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_resize)
        
        self.crear_seccion_carpetas()
        self.crear_seccion_informacion()
        self.crear_seccion_botones()
        self.crear_seccion_progreso()
        self.crear_seccion_log()
    
    def crear_seccion_carpetas(self):
        carpetas_frame = ctk.CTkFrame(self.main_frame)
        carpetas_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(carpetas_frame, text="📂 Carpeta de Origen:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        origen_frame = ctk.CTkFrame(carpetas_frame)
        origen_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.entry_origen = ctk.CTkEntry(origen_frame, textvariable=self.ruta_origen, placeholder_text="Selecciona la carpeta de origen...")
        self.entry_origen.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        btn_origen = ctk.CTkButton(origen_frame, text="Buscar", command=self.seleccionar_origen, width=80)
        btn_origen.pack(side="right", padx=(5, 10), pady=10)
        
        ctk.CTkLabel(carpetas_frame, text="📁 Carpeta de Destino:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        destino_frame = ctk.CTkFrame(carpetas_frame)
        destino_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.entry_destino = ctk.CTkEntry(destino_frame, textvariable=self.ruta_destino, placeholder_text="Selecciona la carpeta de destino...")
        self.entry_destino.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        btn_destino = ctk.CTkButton(destino_frame, text="Buscar", command=self.seleccionar_destino, width=80)
        btn_destino.pack(side="right", padx=(5, 10), pady=10)
    
    def crear_seccion_informacion(self):
        info_frame = ctk.CTkFrame(self.main_frame)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(info_frame, text="📊 Información", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        grid_frame = ctk.CTkFrame(info_frame)
        grid_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_columnconfigure(2, weight=1)
        
        self.label_total = ctk.CTkLabel(grid_frame, text="Total: 0", font=ctk.CTkFont(size=14))
        self.label_total.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        
        self.label_copiados = ctk.CTkLabel(grid_frame, text="Copiados: 0", font=ctk.CTkFont(size=14))
        self.label_copiados.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        self.label_omitidos = ctk.CTkLabel(grid_frame, text="Omitidos: 0", font=ctk.CTkFont(size=14))
        self.label_omitidos.grid(row=0, column=2, padx=10, pady=15, sticky="ew")
    
    def crear_seccion_botones(self):
        botones_frame = ctk.CTkFrame(self.main_frame)
        botones_frame.pack(fill="x", padx=20, pady=10)
        
        btn_container = ctk.CTkFrame(botones_frame)
        btn_container.pack(pady=20)
        
        self.btn_contar = ctk.CTkButton(btn_container, text="📊 Contar Archivos", command=self.contar_archivos_async, width=150, height=40)
        self.btn_contar.pack(side="left", padx=10)
        
        self.btn_copiar = ctk.CTkButton(btn_container, text="🚀 Iniciar Copia", command=self.iniciar_copia, width=150, height=40)
        self.btn_copiar.pack(side="left", padx=10)
        
        self.btn_parar = ctk.CTkButton(btn_container, text="⏹️ Detener", command=self.detener_copia, width=150, height=40, state="disabled")
        self.btn_parar.pack(side="left", padx=10)
        
        self.btn_limpiar = ctk.CTkButton(btn_container, text="🧹 Limpiar Log", command=self.limpiar_log, width=150, height=40)
        self.btn_limpiar.pack(side="left", padx=10)
    
    def crear_seccion_progreso(self):
        progreso_frame = ctk.CTkFrame(self.main_frame)
        progreso_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(progreso_frame, text="⏳ Progreso", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        self.progress_bar = ctk.CTkProgressBar(progreso_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        
        self.label_progreso = ctk.CTkLabel(progreso_frame, text="Listo para comenzar")
        self.label_progreso.pack(pady=(0, 15))
    
    def crear_seccion_log(self):
        log_frame = ctk.CTkFrame(self.main_frame)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(log_frame, text="📝 Registro de Actividad", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        texto_scroll_frame = ctk.CTkFrame(log_frame)
        texto_scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.text_log = ctk.CTkTextbox(texto_scroll_frame, wrap="none")
        self.text_log.pack(side="left", fill="both", expand=True)
        
        log_scrollbar = ctk.CTkScrollbar(texto_scroll_frame, orientation=VERTICAL, command=self.text_log.yview)
        log_scrollbar.pack(side="right", fill="y")
        self.text_log.configure(yscrollcommand=log_scrollbar.set)
    
    def seleccionar_origen(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_origen.set(ruta)
            self.logic.ruta_origen = ruta
            self.log(f"Carpeta de origen seleccionada: {ruta}")
    
    def seleccionar_destino(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_destino.set(ruta)
            self.logic.ruta_destino = ruta
            self.log(f"Carpeta de destino seleccionada: {ruta}")
    
    def contar_archivos_async(self):
        if not self.logic.ruta_origen:
            messagebox.showerror("Error", "Selecciona primero la carpeta de origen")
            return
        threading.Thread(target=self.logic.contar_archivos, daemon=True).start()
    
    def iniciar_copia(self):
        if self.logic.copiando:
            return
        if not self.logic.ruta_origen or not self.logic.ruta_destino:
            messagebox.showerror("Error", "Selecciona las carpetas de origen y destino")
            return
        
        self.logic.copiando = True
        self.btn_contar.configure(state="disabled")
        self.btn_copiar.configure(state="disabled")
        self.btn_parar.configure(state="normal")
        
        threading.Thread(target=self.logic.copiar_archivos, daemon=True).start()
    
    def detener_copia(self):
        if self.logic.copiando:
            self.logic.copiando = False
            self.log("Parando proceso de copia...")
    
    def limpiar_log(self):
        self.text_log.delete("1.0", "end")
    
    def log(self, texto):
        timestamp = time.strftime("%H:%M:%S")
        self.text_log.insert("end", f"[{timestamp}] {texto}\n")
        self.text_log.see("end")
    
    def update_ui(self, total, copiados, omitidos, progreso, label_progreso):
        self.label_total.configure(text=f"Total: {total}")
        self.label_copiados.configure(text=f"Copiados: {copiados}")
        self.label_omitidos.configure(text=f"Omitidos: {omitidos}")
        self.progress_bar.set(progreso)
        self.label_progreso.configure(text=label_progreso)
        self.root.update()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = GestorArchivosGUI()
    app.run()
