import numpy as np
import matplotlib.pyplot as plt

from l1c.src.l1c import l1c
from common.io.readGeodetic import readGeodetic
from common.io.writeToa import readToa

# ----- PLOT 1 COMPARATIVO L1C VS L1B -----

# Inicializamos L1C como si fuera el main para que se ejecuten los códigos

auxdir = r'C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\EODT_Mario\\auxiliary'
indir = r'C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1C\input\gm_alt100_act_150\,C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1C\input\l1b_output'
outdir = r'C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\SHARED\\EODP_TER_2021\\EODP-TS-L1C\\output_Mario'

myL1c = l1c(auxdir, indir, outdir)

# Cogemos el output de l1b (banda VNIR-0)
band = myL1c.globalConfig.bands[0]
toa = myL1c.globalConfig.l1b_toa + band + '.nc'

# Radiancias
from common.io.writeToa import readToa
toa = readToa(myL1c.l1bdir, toa)

# Geolocalización
lat,lon = readGeodetic(myL1c.gmdir,myL1c.globalConfig.gm_geoloc)

# Proyección l1c
lat_l1c,lon_l1c,toa_l1c = myL1c.l1cProjtoa(lat,lon,toa,band)

# Plot
plt.figure(figsize=(10, 7))


# Puntos L1B
plt.scatter(
    lon,
    lat,
    color='red',
    s=8,
    label='L1B'
)


#Puntos L1C
plt.scatter(
    lon_l1c,
    lat_l1c,
    color='blue',
    s=8,
    label='L1C'
)

plt.xlabel('Longitude [deg]')
plt.ylabel('Latitude [deg]')
plt.title('Projection on Ground')
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()

# ----- PLOT SPATIAL SAMPLING DISTANCE -----

# Radio de la Tierra
R = 6371000

# Ploteamos primero las filas y luego las columnas

# FILAS (cogemos la fila intermedia de las 100 que hay)

line = 49
lat_line = lat[line, :]
lon_line = lon[line, :]

# Pasamos los datos obtenidos antes a radianes (estaban en grados)
lat_rad = np.radians(lat_line)
lon_rad = np.radians(lon_line)

# Calculamos la diferencia entre muestras consecutivas
dlat = np.diff(lat_rad)
dlon = np.diff(lon_rad)

# Distancia Harvesine
a = (
    np.sin(dlat / 2) ** 2
    + np.cos(lat_rad[:-1])
    * np.cos(lat_rad[1:])
    * np.sin(dlon / 2) ** 2
)

distance = 2 * R * np.arcsin(np.sqrt(a))


# Resultados del análisis de la fila

print('Line:', line)
print('Number of L1B samples:', len(lat_line))
print('Number of distances:', len(distance))

print('Minimum distance [m]:', np.min(distance))
print('Maximum distance [m]:', np.max(distance))
print('Mean distance [m]:', np.mean(distance))

# Plot
plt.figure(figsize=(10, 5))

plt.plot(
    np.arange(1, len(distance) + 1),
    distance
)

plt.xlabel('Pixel')
plt.ylabel('Spatial sampling distance [m]')
plt.title('L1B Spatial Sampling Distance - Line 50')

plt.ticklabel_format(
    axis='y',
    style='plain',
    useOffset=False
)

plt.grid(True)
plt.tight_layout()

plt.show()


# COLUMNAS (cogemos la columna intermedia de las 150 que hay)

column = 74
lat_column = lat[:, column]
lon_column = lon[:, column]

# Pasamos los datos obtenidos antes a radianes (estaban en grados)
lat_rad = np.radians(lat_column)
lon_rad = np.radians(lon_column)

# Calculamos la diferencia entre muestras consecutivas
dlat = np.diff(lat_rad)
dlon = np.diff(lon_rad)

# Distancia Harvesine

a = (
    np.sin(dlat / 2) ** 2
    + np.cos(lat_rad[:-1])
    * np.cos(lat_rad[1:])
    * np.sin(dlon / 2) ** 2
)

distance_column = 2 * R * np.arcsin(np.sqrt(a))


# Resultados del análisis de la columna

print('Column:', column)
print('Number of L1B samples:', len(lat_column))
print('Number of distances:', len(distance_column))

print('Minimum distance [m]:', np.min(distance_column))
print('Maximum distance [m]:', np.max(distance_column))
print('Mean distance [m]:', np.mean(distance_column))

# Plot
plt.figure(figsize=(10, 5))

plt.plot(
    np.arange(1, len(distance_column) + 1),
    distance_column
)

plt.xlabel('Pixel')
plt.ylabel('Spatial sampling distance [m]')
plt.title('L1B Spatial Sampling Distance - Column 75')

plt.ticklabel_format(
    axis='y',
    style='plain',
    useOffset=False
)

plt.grid(True)
plt.tight_layout()

plt.show()
