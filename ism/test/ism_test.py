from pathlib import Path
import numpy as np
import xarray as xr

dir_a = Path(r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-ISM\output_Mario")
dir_b = Path(r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-ISM\output")

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