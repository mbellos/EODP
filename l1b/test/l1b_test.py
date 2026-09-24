# CROSS VALIDATE L1B OUTPUTS EQUALIZED

# PLOT FROM YOUR OUTPUTS THE EQUALISED OUTPUT VERSUS NOT EQUALISED VERSUS THE TRUTH
# TRUTH = EODP-TS-L1B\input\ism_toa_isrf_VNIR-0.nc
# Comparación de sus outputs con los nuestros de forma numérica una por uno
# Luego, plotear las tres rectas sin ecualizar, ecualizada y la buena (en input, ism_toa_isrf_band.nc) juntas

# Tenemos un multiband imager (un telescopio con un sistema de espejos). La luz entra al telescopio, pasa por filtros... y llega al detector. Adquirimos info. de la parte electromagnética del espectro (400 nm - 1000 nm), lo demás lo filtramos (aunque no es perfecto.
# El sistema no es perfecto (respuesta no homogénea, filtros no ideales, ruido, etc.).
# Para detectar estos primeros fallos, calibramos el instrumento.
# La línea azul es la línea real de energía que llega al instrumento del satélite (la "verdad"-ISRF), la línea roja es la salida del sistema (es la respuesta del instrumento) simplemente por convertir los números digitales a magnitud física, sin recalibration y la línea negra es la respuesta después de calibrar la salida.
# Nunca podremos llegar a esa "verdad", siempre hay un margen de error (delta=ARA-absolute radiometric accuracy). SNR ~ 100
# METER ESTO EN LA MEMORIA Calibration es la forma de entender el comportamiento del instrumento en órbita (utilizas elementos homogeneos para calibrar; desiertos, el sol, mares, etc.)
# y en tierra (a nivel de espectro y radiometric) para compensar los errores que pueda meter

# ----- COMPROBACIÓN OUTPUTS -----

from pathlib import Path
import numpy as np
import xarray as xr

# Directorios de las carpetas a comparar
dir_a = Path(r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\output_Mario")  # Carpeta con los archivos ecualizados
dir_b = Path(r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\output")  # Carpeta con los archivos de referencia


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

                    # Comparativa absoluta
                    diff = np.abs(arr_a - arr_b)

                    if diff.size > 0 and not np.all(np.isnan(diff)):
                        max_diffs.append(np.nanmax(diff))
                        # MMSE
                        rmse_values.append(np.sqrt(np.nanmean((arr_a - arr_b) ** 2)))

        print(f"\nComparación para: {file_a.name}")
        if max_diffs:
            print(f"  • Diferencia máxima absoluta: {max(max_diffs)}")
            print(f"  • Desviación promedio (RMSE): {np.mean(rmse_values):.6e}")
        else:
            print("  ⚠️ No hay datos numéricos comparables o dimensiones incompatibles.")

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