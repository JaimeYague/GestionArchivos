import os
import shutil
import time
import threading
from datetime import timedelta

class GestorArchivosLogic:
    def __init__(self, log_callback=None, update_ui_callback=None):
        self.ruta_origen = ""
        self.ruta_destino = ""
        self.copiando = False
        
        # Funciones callback para comunicar con la interfaz
        self.log = log_callback or (lambda texto: None)
        self.update_ui = update_ui_callback or (lambda total, copiados, omitidos, progreso, label_progreso: None)
    
    def contar_archivos(self):
        self.log("Iniciando conteo de archivos...")
        total = 0
        for root_dir, dirs, files in os.walk(self.ruta_origen):
            total += len(files)
        self.update_ui(total, 0, 0, 0, "Listo para comenzar")
        self.log(f"Total de archivos en origen: {total}")
    
    def copiar_archivos(self):
        self.log("Iniciando copia de archivos...")
        origen = self.ruta_origen
        destino = self.ruta_destino
        
        archivos_origen = []
        for root_dir, dirs, files in os.walk(origen):
            for file in files:
                archivos_origen.append(os.path.join(root_dir, file))
        
        total = len(archivos_origen)
        self.update_ui(total, 0, 0, 0, "Comenzando...")
        
        copiados = 0
        omitidos = 0
        
        start_time = time.time()
        
        for idx, archivo in enumerate(archivos_origen):
            if not self.copiando:
                self.log("Copia detenida por usuario.")
                break
            
            ruta_relativa = os.path.relpath(archivo, origen)
            destino_final = os.path.join(destino, ruta_relativa)
            os.makedirs(os.path.dirname(destino_final), exist_ok=True)
            
            if not os.path.exists(destino_final):
                try:
                    shutil.copy2(archivo, destino_final)
                    copiados += 1
                    self.log(f"Copiado: {ruta_relativa}")
                except Exception as e:
                    self.log(f"Error copiando {ruta_relativa}: {str(e)}")
            else:
                omitidos += 1
                self.log(f"Omitido (ya existe): {ruta_relativa}")
            
            progreso = (idx + 1) / total
            self.update_ui(total, copiados, omitidos, progreso, f"Procesando archivo {idx + 1} de {total}")
        
        elapsed = time.time() - start_time
        self.log(f"Copia finalizada en {str(timedelta(seconds=int(elapsed)))}")
        
        self.copiando = False
        self.update_ui(total, copiados, omitidos, 0, "Listo para comenzar")
