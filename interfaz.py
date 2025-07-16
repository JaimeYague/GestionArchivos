import threading
import time
from tkinter import filedialog, messagebox
import customtkinter as ctk
from gestor_archivos import GestorArchivosLogic

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GestorArchivosGUI:
    def __init__(self):
        self.logic = GestorArchivosLogic(
            log_callback=self.log, 
            update_ui_callback=self.update_ui,
            error_callback=self.mostrar_error
        )
        
        self.root = ctk.CTk()
        self.root.title("Gestor de Archivos - Copia sin Duplicados")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.ruta_origen = ctk.StringVar()
        self.ruta_destino = ctk.StringVar()
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Usar CTkScrollableFrame en lugar de Canvas manual
        self.main_frame = ctk.CTkScrollableFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
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
        
        self.text_log = ctk.CTkTextbox(log_frame, wrap="word", height=200)
        self.text_log.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
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
        """Ejecuta el conteo de archivos en un hilo separado con manejo de errores"""
        if self.logic.copiando:
            messagebox.showwarning("Proceso en curso", "Ya hay un proceso en ejecución")
            return
        
        def wrapper():
            try:
                # Deshabilitar botón durante conteo
                self.root.after(0, lambda: self.btn_contar.configure(state="disabled"))
                self.logic.contar_archivos()
            except Exception as e:
                self.log(f"Error inesperado durante el conteo: {str(e)}")
                self.mostrar_error(f"Error durante el conteo: {str(e)}")
            finally:
                # Siempre rehabilitar el botón
                self.root.after(0, lambda: self.btn_contar.configure(state="normal"))
        
        threading.Thread(target=wrapper, daemon=True).start()
    
    def iniciar_copia(self):
        """Inicia la copia de archivos con validación y manejo de errores"""
        if self.logic.copiando:
            messagebox.showwarning("Proceso en curso", "Ya hay un proceso de copia en ejecución")
            return
        
        # Validación básica antes de iniciar
        if not self.logic.ruta_origen or not self.logic.ruta_destino:
            messagebox.showerror("Error", "Selecciona las carpetas de origen y destino")
            return
        
        def wrapper():
            try:
                self.logic.copiando = True
                # Cambiar estado de botones de forma thread-safe
                self.root.after(0, self.deshabilitar_botones_copia)
                
                self.logic.copiar_archivos()
                
            except Exception as e:
                self.log(f"Error inesperado durante la copia: {str(e)}")
                self.mostrar_error(f"Error durante la copia: {str(e)}")
            finally:
                # Siempre restaurar estado de botones
                self.root.after(0, self.rehabilitar_botones_copia)
        
        threading.Thread(target=wrapper, daemon=True).start()
    
    def detener_copia(self):
        """Detiene la copia de forma segura"""
        if self.logic.copiando:
            self.logic.detener_copia()
            self.log("Solicitando detención del proceso...")
            # El botón se rehabilitará automáticamente cuando termine el proceso
    
    def deshabilitar_botones_copia(self):
        """Deshabilita botones durante la copia"""
        self.btn_contar.configure(state="disabled")
        self.btn_copiar.configure(state="disabled")
        self.btn_parar.configure(state="normal")
    
    def rehabilitar_botones_copia(self):
        """Rehabilita botones después de la copia"""
        self.btn_contar.configure(state="normal")
        self.btn_copiar.configure(state="normal")
        self.btn_parar.configure(state="disabled")
    
    def limpiar_log(self):
        """Limpia el registro de actividad"""
        self.text_log.delete("1.0", "end")
        self.log("Log limpiado")
    
    def log(self, texto):
        """Añade una entrada al log con timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        mensaje = f"[{timestamp}] {texto}\n"
        
        # Insertar de forma thread-safe
        self.root.after(0, lambda: self._insertar_log(mensaje))
    
    def _insertar_log(self, mensaje):
        """Inserta mensaje en el log (debe ejecutarse en el hilo principal)"""
        self.text_log.insert("end", mensaje)
        self.text_log.see("end")
        
        # Limitar el log a las últimas 1000 líneas para evitar consumo excesivo de memoria
        lines = self.text_log.get("1.0", "end").split('\n')
        if len(lines) > 1000:
            self.text_log.delete("1.0", f"{len(lines)-1000}.0")
    
    def update_ui(self, total, copiados, omitidos, progreso, label_progreso):
        """Actualiza la interfaz de usuario de forma thread-safe"""
        def actualizar():
            self.label_total.configure(text=f"Total: {total}")
            self.label_copiados.configure(text=f"Copiados: {copiados}")
            self.label_omitidos.configure(text=f"Omitidos: {omitidos}")
            self.progress_bar.set(progreso)
            self.label_progreso.configure(text=label_progreso)
        
        # Programar actualización en el hilo principal
        self.root.after(0, actualizar)
    
    def mostrar_error(self, mensaje):
        """Muestra errores de forma thread-safe"""
        def mostrar():
            messagebox.showerror("Error", mensaje)
        
        self.root.after(0, mostrar)
    
    def run(self):
        """Inicia la aplicación"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error crítico en la aplicación: {str(e)}")
            messagebox.showerror("Error Crítico", f"Error crítico en la aplicación: {str(e)}")

if __name__ == "__main__":
    try:
        app = GestorArchivosGUI()
        app.run()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {str(e)}")
        messagebox.showerror("Error de Inicio", f"No se pudo iniciar la aplicación: {str(e)}")
