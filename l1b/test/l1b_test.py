# CROSS VALIDATE L1B OUTPUTS EQUALIZED

# PLOT FROM YOUR OUTPUTS THE EQUALISED OUTPUT VERSUS NOT EQUALISED VERSUS THE TRUTH
# TRUTH = EODP-TS-L1B\input\ism_toa_isrf_VNIR-0.nc
# Comparación de sus outputs con los nuestros de forma numérica una por uno
# Luego, plotear las tres rectas sin ecualizar, ecualizada y la buena (en input, ism_toa_isrf_band.nc) juntas

# Tenemos un multiband imager (un telescopio con un sistema de espejos). La luz entra al telescopio, pasa por filtros... y llega al detector. Adquirimos info. de la parte electromagnética del espectro (400 nm - 1000 nm), lo demás lo filtramos (aunque no es perfecto.
# El sistema no es perfecto (respuesta no homogénea, filtros no ideales, ruido, etc.).
# Para detectar estos primeros fallos, calibramos el instrumento.
# La línea azul es la línea real de energía que llega al instrumento del satélite (la "verdad"), la línea roja es la salida del sistema simplemente por convertir los números digitales a magnitud física, sin recalibration y la línea negra es la respuesta después de calibrar la salida.
# Nunca podremos llegar a esa "verdad", siempre hay un margen de error (delta=ARA-absolute radiometric accuracy). SNR ~ 100

# COMPROBACIÓN OUTPUTS

from pathlib import Path
import numpy as np
import xarray as xr

dir_a = Path(r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\output_Mario")  # Carpeta reducida (los 4 archivos)
dir_b = Path(r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\output")  # Carpeta principal con más archivos

for file_a in dir_a.glob("*.nc"):
    file_b = dir_b / file_a.name
    if not file_b.exists():
        print(f"❌ {file_a.name}: No encontrado en carpeta B")
        continue

    with xr.open_dataset(file_a) as ds_a, xr.open_dataset(file_b) as ds_b:
        max_diffs = []
        rmse_values = []

        for var in ds_a.data_vars:
            if var in ds_b.data_vars:
                arr_a, arr_b = ds_a[var].values, ds_b[var].values

                # Comprobar que tengan las mismas dimensiones antes de restar
                if arr_a.shape == arr_b.shape and np.issubdtype(arr_a.dtype, np.number):
                    diff = np.abs(arr_a - arr_b)

                    if diff.size > 0 and not np.all(np.isnan(diff)):
                        max_diffs.append(np.nanmax(diff))
                        rmse_values.append(np.sqrt(np.nanmean((arr_a - arr_b) ** 2)))

        print(f"\n📄 Comparación para: {file_a.name}")
        if max_diffs:
            print(f"  • Diferencia máxima absoluta: {max(max_diffs)}")
            print(f"  • Desviación promedio (RMSE): {np.mean(rmse_values):.6e}")
        else:
            print("  ⚠️ No hay datos numéricos comparables o dimensiones incompatibles.")

# PLOT COMPARATIVO

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os

# =====================================================================
# CONFIGURACIÓN: Reemplaza con tus rutas y nombres reales
# =====================================================================

# 1. Rutas exactas a tus 3 archivos .nc (usa r'' para rutas de Windows)
file_paths = {
    'ref': r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\input\ism_toa_isrf_VNIR-0.nc",  # Referencia azul
    'no_eq': r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\output_Mario_noteq\l1b_toa_VNIR-0.nc",  # Sin eq roja
    'with_eq': r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\output_Mario\l1b_toa_VNIR-0.nc",  # Con eq negra
}

# 2. Nombre de la variable que confirmamos que es 'toa'
toa_var_name = 'toa'

# 3. CRUCIAL: ¿Qué línea (alt_lines) quieres visualizar?
# Tu gráfico actual (image_1.png) muestra 100 líneas (0-100).
# Para obtener UN gráfico de líneas como image_0.png, debemos elegir UN índice.
# Por defecto, elegimos la primera línea (índice 0).
line_index_to_plot = 50

# =====================================================================
# PROCESAMIENTO
# =====================================================================

print(f"Iniciando el procesamiento para generar el gráfico de líneas...")
print(f"Visualizando la línea índice: {line_index_to_plot} (de la dimensión 'alt_lines')")

# Diccionario para almacenar los perfiles 1D extraídos
data_profiles = {}

# Cargar y extraer el perfil 1D de cada archivo
for name, path in file_paths.items():
    print(f"  > Procesando archivo: {os.path.basename(path)}")
    try:
        # 1. Abrir el dataset
        with xr.open_dataset(path) as ds:
            # 2. Extraer la variable 2D 'toa' (dimensiones presumiblemente alt_lines, act_columns)
            toa_2d = ds[toa_var_name]

            # 3. CRUCIAL: Convertir 2D en 1D. Seleccionamos UNA sola línea.
            # Asumimos que la primera dimensión es 'alt_lines' y la segunda 'act_columns'
            # .isel() selecciona por índice.
            profile_1d = toa_2d.isel(alt_lines=line_index_to_plot)

            # 4. Guardar los valores numéricos y el eje X
            data_profiles[name] = profile_1d.values

            # Si es la primera ejecución, guardamos el eje X (píxeles)
            if 'x_axis' not in data_profiles:
                data_profiles['x_axis'] = np.arange(profile_1d.size)

    except Exception as e:
        print(f"❌ Error al abrir o leer el archivo {os.path.basename(path)}: {e}")
        exit()

# Verificar que los datos sean compatibles
print("  > Verificando consistencia de datos...")
ref_size = data_profiles['x_axis'].size
for name in ['ref', 'no_eq', 'with_eq']:
    if data_profiles[name].size != ref_size:
        print(
            f"❌ Error: El perfil del archivo '{name}' tiene un tamaño diferente ({data_profiles[name].size}) que la referencia ({ref_size}).")
        exit()

# =====================================================================
# GRÁFICA (REPLICANDO FIELMENTE ESTILO image_0.png)
# =====================================================================

print("  > Generando gráfica de líneas superpuestas...")
plt.figure(figsize=(12, 7))  # Tamaño adecuado para ver los detalles

# Eje X común
x = data_profiles['x_axis']

# 1. Graficar las 3 líneas CON LOS COLORES Y ORDEN EXACTOS de image_0.png
# La referencia azul se grafica primero para estar al fondo si es suave
plt.plot(x, data_profiles['ref'], label='TOA after the ISRF', color='blue', linestyle='-')

# La línea sin ecualización roja (con ruido)
plt.plot(x, data_profiles['no_eq'], label='TOA L1B no eq', color='red', linestyle='-')

# La línea con ecualización negra (corregida)
plt.plot(x, data_profiles['with_eq'], label='TOA L1B with eq', color='black', linestyle='-')

# 2. Configuración de títulos y etiquetas EXACTAS de image_0.png
plt.title(f'Effect of the Equalization for VNIR-0 (Line {line_index_to_plot})', fontsize=14)
plt.ylabel('TOA [mW/m2/sr]', fontsize=12)
plt.xlabel('ACT pixel [-]', fontsize=12)

# 3. Estilo general: Rejilla, Leyenda en la esquina superior izquierda
plt.legend(loc='upper left', fontsize=10)
plt.grid(True, which='both', linestyle='-', color='grey', alpha=0.5)

# 4. Ajustar márgenes
plt.tight_layout()

# Mostrar la gráfica
print("\n✅ Script completado. Mostrando gráfica de líneas.")
plt.show()