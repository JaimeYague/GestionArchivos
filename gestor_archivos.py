import os
import shutil
import time
import threading
from datetime import timedelta

class GestorArchivosLogic:
    def __init__(self, log_callback=None, update_ui_callback=None, error_callback=None):
        self.ruta_origen = ""
        self.ruta_destino = ""
        self.copiando = False
        
        # Funciones callback para comunicar con la interfaz
        self.log = log_callback or (lambda texto: None)
        self.update_ui = update_ui_callback or (lambda total, copiados, omitidos, progreso, label_progreso: None)
        self.error_callback = error_callback or (lambda error: None)
    
    def validar_rutas(self):
        """Valida que las rutas sean accesibles antes de proceder"""
        if not self.ruta_origen:
            raise ValueError("Debe seleccionar una carpeta de origen")
        
        if not self.ruta_destino:
            raise ValueError("Debe seleccionar una carpeta de destino")
        
        if not os.path.exists(self.ruta_origen):
            raise FileNotFoundError(f"La carpeta de origen no existe: {self.ruta_origen}")
        
        if not os.access(self.ruta_origen, os.R_OK):
            raise PermissionError(f"Sin permisos de lectura en: {self.ruta_origen}")
        
        # Crear carpeta destino si no existe
        try:
            os.makedirs(self.ruta_destino, exist_ok=True)
        except Exception as e:
            raise PermissionError(f"No se puede crear la carpeta destino: {str(e)}")
        
        if not os.access(self.ruta_destino, os.W_OK):
            raise PermissionError(f"Sin permisos de escritura en: {self.ruta_destino}")
    
    def contar_archivos(self):
        """Cuenta los archivos en la carpeta origen con manejo de errores"""
        try:
            self.log("Iniciando conteo de archivos...")
            
            # Validar rutas antes de proceder
            self.validar_rutas()
            
            total = 0
            archivos_procesados = 0
            
            for root_dir, dirs, files in os.walk(self.ruta_origen):
                # Verificar si se puede acceder al directorio
                try:
                    total += len(files)
                    archivos_procesados += len(files)
                    
                    # Actualizar progreso cada 100 archivos
                    if archivos_procesados % 100 == 0:
                        self.update_ui(archivos_procesados, 0, 0, 0, f"Contando... {archivos_procesados} archivos")
                        
                except PermissionError:
                    self.log(f"Sin permisos para acceder a: {root_dir}")
                    continue
                except Exception as e:
                    self.log(f"Error accediendo a {root_dir}: {str(e)}")
                    continue
            
            self.update_ui(total, 0, 0, 0, "Listo para comenzar")
            self.log(f"Conteo completado. Total de archivos: {total}")
            
        except Exception as e:
            self.log(f"Error durante el conteo: {str(e)}")
            self.error_callback(f"Error durante el conteo: {str(e)}")
            self.update_ui(0, 0, 0, 0, "Error en conteo")
    
    def copiar_archivos(self):
        """Copia archivos con manejo robusto de errores"""
        try:
            self.log("Iniciando copia de archivos...")
            
            # Validar rutas antes de proceder
            self.validar_rutas()
            
            origen = self.ruta_origen
            destino = self.ruta_destino
            
            # Obtener lista de archivos
            archivos_origen = []
            self.log("Escaneando archivos...")
            
            for root_dir, dirs, files in os.walk(origen):
                for file in files:
                    if not self.copiando:  # Verificar si se debe detener
                        self.log("Escaneo detenido por usuario.")
                        return
                    
                    try:
                        archivo_path = os.path.join(root_dir, file)
                        # Verificar que el archivo sea accesible
                        if os.access(archivo_path, os.R_OK):
                            archivos_origen.append(archivo_path)
                    except Exception as e:
                        self.log(f"Error accediendo a {file}: {str(e)}")
                        continue
            
            total = len(archivos_origen)
            self.log(f"Se procesarán {total} archivos")
            self.update_ui(total, 0, 0, 0, "Comenzando copia...")
            
            copiados = 0
            omitidos = 0
            errores = 0
            
            start_time = time.time()
            
            for idx, archivo in enumerate(archivos_origen):
                if not self.copiando:
                    self.log("Copia detenida por usuario.")
                    break
                
                try:
                    ruta_relativa = os.path.relpath(archivo, origen)
                    destino_final = os.path.join(destino, ruta_relativa)
                    
                    # Crear directorio destino si no existe
                    directorio_destino = os.path.dirname(destino_final)
                    os.makedirs(directorio_destino, exist_ok=True)
                    
                    if not os.path.exists(destino_final):
                        try:
                            shutil.copy2(archivo, destino_final)
                            copiados += 1
                            self.log(f"Copiado: {ruta_relativa}")
                        except PermissionError:
                            self.log(f"Sin permisos para copiar: {ruta_relativa}")
                            errores += 1
                        except OSError as e:
                            self.log(f"Error de sistema copiando {ruta_relativa}: {str(e)}")
                            errores += 1
                        except Exception as e:
                            self.log(f"Error inesperado copiando {ruta_relativa}: {str(e)}")
                            errores += 1
                    else:
                        omitidos += 1
                        self.log(f"Omitido (ya existe): {ruta_relativa}")
                    
                    # Actualizar progreso
                    progreso = (idx + 1) / total
                    self.update_ui(total, copiados, omitidos, progreso, 
                                 f"Procesando {idx + 1}/{total} - Copiados: {copiados}, Omitidos: {omitidos}")
                    
                except Exception as e:
                    self.log(f"Error procesando archivo {archivo}: {str(e)}")
                    errores += 1
                    continue
            
            elapsed = time.time() - start_time
            self.log(f"Proceso finalizado en {str(timedelta(seconds=int(elapsed)))}")
            self.log(f"Resumen: {copiados} copiados, {omitidos} omitidos, {errores} errores")
            
        except Exception as e:
            self.log(f"Error crítico durante la copia: {str(e)}")
            self.error_callback(f"Error crítico durante la copia: {str(e)}")
            
        finally:
            # Siempre restaurar estado
            self.copiando = False
            self.update_ui(0, 0, 0, 0, "Proceso terminado")
    
    def detener_copia(self):
        """Detiene la copia de forma segura"""
        if self.copiando:
            self.copiando = False
            self.log("Solicitando detención del proceso...")