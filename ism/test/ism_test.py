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

# COMPARATIVA ANALYTIC VS READ TABLA

import numpy as np

# Constantes físicas (mismos valores que en el archivo config)
h = 6.62607015e-34  # [J*s] Constante de Planck
c = 299792458.0  # [m/s] Velocidad de la luz


def compute_analytic_pixel_from_config(L_rad, band_idx, cfg, include_dark_signal=False):
    """
    Calcula el valor analítico ideal para un píxel dada su radiancia de entrada.
    :param L_rad: Radiancia espectral en [mW/sr/m2]
    :param band_idx: Índice de la banda (0: VNIR-0, 1: VNIR-1, 2: VNIR-2, 3: VNIR-3)
    :param cfg: Instancia de la clase ismConfig
    :param include_dark_signal: Indica si se suma el offset medio de corriente en oscuro (Sd)
    """
    wv_m = cfg.wv[band_idx]  # Longitud de onda en metros [m]

    # 1. Radiancia a Irradiancia [mW/m2] (rad2Irrad)
    irrad = cfg.Tr * L_rad * (np.pi / 4.0) * ((cfg.D / cfg.f) ** 2)

    # 2. Irradiancia a Fotones [ph] (irrad2Phot)
    area_pix = cfg.pix_size ** 2
    e_in = (irrad * 1e-3) * area_pix * cfg.t_int
    e_ph = (h * c) / wv_m
    photons = e_in / e_ph

    # 3. Fotones a Electrones [e-] (phot2Electr)
    electrons_photo = photons * cfg.QE

    # 3.b. Dark Signal (darkSignal)
    if include_dark_signal:
        Sd = cfg.ds_A_coeff * ((cfg.T / cfg.Tref) ** 3) * np.exp(-cfg.ds_B_coeff * ((1.0 / cfg.T) - (1.0 / cfg.Tref)))
        electrons_total = electrons_photo + Sd
    else:
        electrons_total = electrons_photo

    # Aplicación del límite por Full Well Capacity (FWC)
    electrons_sat = min(electrons_total, cfg.FWC)

    # 4. Electrones a Voltaje [V] (electr2Volt)
    volts = electrons_sat * cfg.OCF * cfg.ADC_gain

    # 5. Digitalización [DN] (digitisation)
    max_dn = (2 ** cfg.bit_depth) - 1
    dn_float = np.round((volts / (cfg.max_voltage - cfg.min_voltage)) * max_dn)
    dn = int(np.clip(dn_float, 0, max_dn))

    return {
        'Radiance [mW/sr/m2]': L_rad,
        'Irradiance [mW/m2]': irrad,
        'Photons [ph]': photons,
        'Electrons (Photo) [e-]': electrons_photo,
        'Electrons (Final) [e-]': electrons_sat,
        'Voltage [V]': volts,
        'DN [DN]': dn
    }

# Instanciamos objeto de configuración para los parámetros del instrumento
from config.ismConfig import ismConfig
cfg = ismConfig()

radiances_50_75 = [68.92, 197.72, 342.87, 403.07]  # [VNIR-0, VNIR-1, VNIR-2, VNIR-3]
band_names = ['VNIR-0', 'VNIR-1', 'VNIR-2', 'VNIR-3']

for idx, band_name in enumerate(band_names):
    L = radiances_50_75[idx]
    res = compute_analytic_pixel_from_config(L, idx, cfg, include_dark_signal=False)
    print(f"=== {band_name} Analytic ===")
    for k, v in res.items():
        print(f"  {k}: {v}")