# CROSS VALIDATE L1B OUTPUTS EQUALIZED

# PLOT FROM YOUR OUTPUTS THE EQUALISED OUTPUT VERSUS NOT EQUALISED VERSUS THE TRUTH
# TRUTH = EODP-TS-L1B\input\ism_toa_isrf_VNIR-0.nc

# ----- COMPROBACIÓN OUTPUTS -----

from pathlib import Path
import numpy as np
import xarray as xr

# Directorios de las carpetas a comparar
dir_a = Path(r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\output_Mario")  # Carpeta con los archivos ecualizados
dir_b = Path(r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\output")  # Carpeta con los archivos de referencia


files_a = {f.name: f for f in dir_a.glob("*.nc")}
files_b = {f.name: f for f in dir_b.glob("*.nc")}

# 1. Comprobar archivos que existen solo en una carpeta
only_in_a = files_a.keys() - files_b.keys()
only_in_b = files_b.keys() - files_a.keys()

if only_in_a:
    print(f"⚠️ Archivos solo en carpeta A: {list(only_in_a)}")
if only_in_b:
    print(f"⚠️ Archivos solo en carpeta B: {list(only_in_b)}")

# 2. Comparar archivos coincidentes
common_files = sorted(files_a.keys() & files_b.keys())

for filename in common_files:
    file_a = files_a[filename]
    file_b = files_b[filename]

    print(f"\n──────────────────────────────────────────────")
    print(f"📄 Comparando: {filename}")

    with xr.open_dataset(file_a) as ds_a, xr.open_dataset(file_b) as ds_b:
        has_comparable_data = False

        # Variables en A que no están en B
        missing_vars = set(ds_a.data_vars) - set(ds_b.data_vars)
        if missing_vars:
            print(f"  ⚠️ Variables faltantes en B: {missing_vars}")

        for var in ds_a.data_vars:
            if var not in ds_b.data_vars:
                continue

            arr_a, arr_b = ds_a[var].values, ds_b[var].values

            # Validar que sean datos numéricos
            if not np.issubdtype(arr_a.dtype, np.number):
                continue

            # Validar dimensiones
            if arr_a.shape != arr_b.shape:
                print(f"  ❌ {var}: Formas incompatibles (A: {arr_a.shape} vs B: {arr_b.shape})")
                continue

            diff = np.abs(arr_a - arr_b)

            if diff.size > 0 and not np.all(np.isnan(diff)):
                max_diff = np.nanmax(diff)
                rmse = np.sqrt(np.nanmean((arr_a - arr_b) ** 2))
                has_comparable_data = True

                # Reporte por variable (marcar en verde si son idénticas)
                status = "✅ Idénticas" if max_diff == 0 else "⚠️ Hay diferencias"
                print(f"  • Variable [{var}]: {status}")
                print(f"      - Dif. Máx: {max_diff:.6e}")
                print(f"      - RMSE:     {rmse:.6e}")

        if not has_comparable_data:
            print("  ⚠️ No se pudieron comparar variables numéricas coincidentes.")

# ----- PLOT COMPARATIVO -----

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os

# Rutas exactas a los 3 archivos a plotear
file_paths = {
    'ref': r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\input\ism_toa_isrf_VNIR-0.nc",  # Referencia azul
    'no_eq': r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\output_Mario_noteq\l1b_toa_VNIR-0.nc",  # Sin eq roja
    'with_eq': r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\output_Mario\l1b_toa_VNIR-0.nc",  # Con eq negra
}

# Nombre de la variable a plotear
toa_var_name = 'toa'

# El gráfico actual muestra 100 líneas (0-100).
# Para obtener un gráfico de líneas, debemos elegir un índice.
line_index_to_plot = 50

print(f"Visualizando la línea índice: {line_index_to_plot} (de la dimensión 'alt_lines')")

# Diccionario para almacenar los perfiles 1D extraídos
data_profiles = {}

# Cargar y extraer el perfil 1D de cada archivo
for name, path in file_paths.items():
    print(f"  > Procesando archivo: {os.path.basename(path)}")
    try:
        # Abrir el dataset
        with xr.open_dataset(path) as ds:
            # Extraer la variable 2D 'toa' (dimensiones presumiblemente alt_lines, act_columns)
            toa_2d = ds[toa_var_name]

            # Convertir 2D en 1D. Seleccionamos UNA sola línea.
            profile_1d = toa_2d.isel(alt_lines=line_index_to_plot)

            # Guardar los valores numéricos y el eje X
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

# Gráfica
plt.figure(figsize=(12, 7))  # Tamaño adecuado para ver los detalles

# Eje X común
x = data_profiles['x_axis']

# La referencia azul se grafica primero para estar al fondo si es suave
plt.plot(x, data_profiles['ref'], label='TOA after the ISRF', color='blue', linestyle='-')

# La línea sin ecualización roja (con ruido)
plt.plot(x, data_profiles['no_eq'], label='TOA L1B no eq', color='red', linestyle='-')

# La línea con ecualización negra (corregida)
plt.plot(x, data_profiles['with_eq'], label='TOA L1B with eq', color='black', linestyle='-')

# Títulos y etiquetas
plt.title(f'Effect of the Equalization for VNIR-0 (Line {line_index_to_plot})', fontsize=14)
plt.ylabel('TOA [mW/m2/sr]', fontsize=12)
plt.xlabel('ACT pixel [-]', fontsize=12)
plt.legend(loc='upper left', fontsize=10)
plt.grid(True, which='both', linestyle='-', color='grey', alpha=0.5)
plt.tight_layout()
plt.savefig(
    r"C:\Users\mbell\OneDrive\Escritorio\EODT\EODT_Mario\l1b\test\eq_test.png", dpi=300, bbox_inches="tight"
)
plt.show()