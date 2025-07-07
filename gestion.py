import os
import shutil
import time
from datetime import timedelta

# ⚠️ CAMBIA ESTAS DOS RUTAS
RUTA_ORIGEN = r"E:\FOTOS\Skateday"  # ← Cambia esto
RUTA_DESTINO = r"C:\PruebaGestion"  # ← Cambia esto (puede ser tu disco externo)

def contar_archivos(origen):
    total = 0
    for carpeta_raiz, _, archivos in os.walk(origen):
        total += len(archivos)
    return total

def copiar_fotos(origen, destino):
    inicio = time.time()  # ⏱️ Marcar tiempo de inicio

    total_archivos = contar_archivos(origen)
    copiados = 0
    procesados = 0

    for carpeta_raiz, _, archivos in os.walk(origen):
        for archivo in archivos:
            procesados += 1
            ruta_original = os.path.join(carpeta_raiz, archivo)
            ruta_relativa = os.path.relpath(ruta_original, origen)
            ruta_final = os.path.join(destino, ruta_relativa)

            os.makedirs(os.path.dirname(ruta_final), exist_ok=True)

            if not os.path.exists(ruta_final):
                try:
                    shutil.copy2(ruta_original, ruta_final)
                    copiados += 1
                    print(f"[{procesados}/{total_archivos}] ✅ Copiado: {ruta_relativa}")
                except Exception as e:
                    print(f"[{procesados}/{total_archivos}] ❌ Error al copiar {ruta_relativa}: {e}")
            else:
                print(f"[{procesados}/{total_archivos}] ⏩ Ya existe, omitido: {ruta_relativa}")

    fin = time.time()
    transcurrido = fin - inicio
    tiempo_legible = str(timedelta(seconds=int(transcurrido)))

    print(f"\n✅ Finalizado: {copiados} archivos copiados de {total_archivos} encontrados.")
    print(f"⏱️ Tiempo total transcurrido: {tiempo_legible} ({transcurrido:.2f} segundos)")

if __name__ == "__main__":
    if not os.path.exists(RUTA_ORIGEN):
        print("❌ La ruta de origen no existe.")
    elif not os.path.exists(RUTA_DESTINO):
        print("❌ La ruta de destino no existe. Conecta tu disco externo o crea la carpeta.")
    else:
        copiar_fotos(RUTA_ORIGEN, RUTA_DESTINO)