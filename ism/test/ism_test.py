from pathlib import Path
import numpy as np
import xarray as xr

# Directorios de las carpetas a comparar
dir_a = Path(r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-ISM\output_Mario")
dir_b = Path(r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-ISM\output")

# Nos quedamos solo con los qrchivos con extensión .nc
files_a = {f.name: f for f in dir_a.glob("*.nc")}
files_b = {f.name: f for f in dir_b.glob("*.nc")}

# Comprobar archivos que existen solo en una carpeta (no podrán compararse)
only_in_a = files_a.keys() - files_b.keys()
only_in_b = files_b.keys() - files_a.keys()


if only_in_a:
    print(f"Files only in A: {list(only_in_a)}")
if only_in_b:
    print(f"Files only in B: {list(only_in_b)}")

# Comparamos archivos coincidentes
common_files = sorted(files_a.keys() & files_b.keys())

for filename in common_files:
    file_a = files_a[filename]
    file_b = files_b[filename]

    print(f"──────────────────────────────────────────────")
    print(f"Comparing: {filename}")

    with xr.open_dataset(file_a) as ds_a, xr.open_dataset(file_b) as ds_b:
        has_comparable_data = False

        # Miramos si hay variables diferentes en los archivos generados
        # Variables en A que no están en B
        missing_vars = set(ds_a.data_vars) - set(ds_b.data_vars)
        if missing_vars:
            print(f"Missing variables in B: {missing_vars}")

        for var in ds_a.data_vars:
            if var not in ds_b.data_vars:
                continue

            arr_a, arr_b = ds_a[var].values, ds_b[var].values

            # Validamos que sean datos numéricos
            if not np.issubdtype(arr_a.dtype, np.number):
                continue

            # Validamos dimensiones
            if arr_a.shape != arr_b.shape:
                print(f"{var}: Different dimensions (A: {arr_a.shape} vs B: {arr_b.shape})")
                continue

            # Para cada par de archivos, calculamos su error absoluto y su RMSE
            diff = np.abs(arr_a - arr_b)

            if diff.size > 0 and not np.all(np.isnan(diff)):
                max_diff = np.nanmax(diff)
                rmse = np.sqrt(np.nanmean((arr_a - arr_b) ** 2))
                has_comparable_data = True

                # Conclusiones para cada archivo
                status = "Identical" if max_diff == 0 else "Different"
                print(f"  • Variable [{var}]: {status}")
                print(f"      - Max. Diff.: {max_diff:.6e}")
                print(f"      - RMSE:     {rmse:.6e}")

        if not has_comparable_data:
            print("Could not compare matching numerical variables")