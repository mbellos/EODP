from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

# Ruta a la carpeta donde se encuentran los archivos .nc
folder_path = Path(
    r"C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1B\output_E2E"
)

# Buscamos todos los archivos l1b_toa_VNIR-*.nc
nc_files = sorted(folder_path.glob("l1b_toa_VNIR-*.nc"))

# Generamos el histograma
for file_path in nc_files:
    print(f"Generando histograma para: {file_path.name}")

    with xr.open_dataset(file_path) as ds:
        # Detectamos la variable de datos
        var_name = "toa" if "toa" in ds.data_vars else list(ds.data_vars)[0]

        # Extraemos y aplanamos a vector 1D
        data = ds[var_name].values.flatten()
        data = data[~np.isnan(data)]

        # Configuramos la figura con marco recuadrado
        fig, ax = plt.subplots(figsize=(8, 5.5), dpi=150)

        counts, bins, patches = ax.hist(
            data,
            bins=180,  # Bins necesarios para imitar la resolución de QGIS
            histtype="bar",
            facecolor="none",  # Sin relleno interno
            edgecolor="#3a3a52",  # Tono gris/azul oscuro del contorno de QGIS
            linewidth=0.6,
            label="Band 1",
        )

        ax.set_title(f"Histogram {file_path.stem.replace('l1b_toa_', '')}", fontsize=13, fontweight="bold", pad=10)
        ax.set_xlabel("Pixel Value", fontsize=10, fontweight="bold", labelpad=5)
        ax.set_ylabel("Frequency", fontsize=10, fontweight="bold", labelpad=5)

        # Marco cerrado completo alrededor de la gráfica
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("black")
            spine.set_linewidth(0.8)

        # Rejilla de líneas negras finas
        ax.grid(
            True, which="major", color="black", linestyle="-", linewidth=0.5
        )
        ax.set_axisbelow(True)

        # Marcas de graduación (ticks) principales y secundarias
        ax.minorticks_on()
        ax.tick_params(
            axis="both",
            which="major",
            direction="inout",
            length=5,
            width=0.8,
            colors="black",
            labelsize=9,
        )
        ax.tick_params(
            axis="both",
            which="minor",
            direction="inout",
            length=3,
            width=0.5,
            colors="black",
        )

        # El eje Y arranca exactamente en 0
        ax.set_ylim(bottom=0)

        # Leyenda inferior centrada
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.12),
            frameon=False,
            fontsize=9,
        )

        plt.tight_layout()

        # Guardar imagen
        output_img = folder_path / f"histogram_{file_path.stem}.png"
        plt.savefig(output_img, dpi=300, bbox_inches="tight")
        plt.show()
        plt.close()