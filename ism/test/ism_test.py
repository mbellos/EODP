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

# Constantes físicas
h = 6.62607015e-34  # [J*s]
c = 299792458.0     # [m/s]


def compute_analytic_pixel_from_config(
    L_rad, band_idx, cfg, include_dark_signal=False
):
    """
    Calcula el valor analítico ideal para un píxel dada su radiancia.
    Devuelve también los factores de conversión de cada etapa.
    """

    wv_m = cfg.wv[band_idx]

    # 1. Radiancia -> Irradiancia
    factor_rad2irrad = cfg.Tr * (np.pi / 4.0) * ((cfg.D / cfg.f) ** 2)
    irrad = factor_rad2irrad * L_rad

    # 2. Irradiancia -> Fotones
    area_pix = cfg.pix_size ** 2
    e_ph = (h * c) / wv_m

    # Factor de conversión: mW/m² -> fotones
    factor_irrad2phot = (1e-3 * area_pix * cfg.t_int) / e_ph
    e_in = (irrad * 1e-3) * area_pix * cfg.t_int
    photons = e_in / e_ph

    # 3. Fotones -> Electrones foto
    factor_phot2electr = cfg.QE
    electrons_photo = photons * factor_phot2electr

    # 3.b. Dark Signal
    Sd = cfg.ds_A_coeff * ((cfg.T / cfg.Tref) ** 3) * np.exp(
        -cfg.ds_B_coeff * ((1.0 / cfg.T) - (1.0 / cfg.Tref))
    )

    if include_dark_signal:
        electrons_total = electrons_photo + Sd
    else:
        electrons_total = electrons_photo

    # 4. Full Well Capacity
    electrons_sat = min(electrons_total, cfg.FWC)

    # 5. Electrones -> Voltaje (no saturamos al valor FWC para ver qué valores habría si no hubiera esta saturación)
    factor_electr2volt = cfg.OCF * cfg.ADC_gain
    volts = electrons_total * factor_electr2volt

    # 6. Voltaje -> DN
    max_dn = (2 ** cfg.bit_depth) - 1
    voltage_range = cfg.max_voltage - cfg.min_voltage

    factor_volt2dn = max_dn / voltage_range
    dn_float = np.round(volts * factor_volt2dn)
    dn = int(dn_float)

    # Resultados
    return {
        'Radiance [mW/sr/m2]': L_rad,

        'Factor rad2Irrad': factor_rad2irrad,
        'Irradiance [mW/m2]': irrad,

        'Factor irrad2Phot [ph/(mW/m2)]': factor_irrad2phot,
        'Photons [ph]': photons,

        'Factor phot2Electr [e-/ph]': factor_phot2electr,
        'Electrons (Photo) [e-]': electrons_photo,

        'Electrons before FWC [e-]': electrons_total,
        'Electrons (Sat.) [e-]': electrons_sat,

        'Factor electr2Volt [V/e-]': factor_electr2volt,
        'Voltage [V]': volts,

        'Factor volt2DN [DN/V]': factor_volt2dn,
        'DN [DN]': dn
    }


# Configuración del instrumento
from config.ismConfig import ismConfig

cfg = ismConfig()

radiances_50_75 = [68.92, 197.72, 342.87, 403.07]
band_names = ['VNIR-0', 'VNIR-1', 'VNIR-2', 'VNIR-3']

for idx, band_name in enumerate(band_names):
    L = radiances_50_75[idx]

    res = compute_analytic_pixel_from_config(
        L, idx, cfg, include_dark_signal=False
    )

    print(f"\n=== {band_name} Analytic ===")
    for k, v in res.items():
        print(f"  {k}: {v}")

