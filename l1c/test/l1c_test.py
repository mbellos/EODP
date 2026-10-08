import numpy as np
import matplotlib.pyplot as plt

from l1c.src.l1c import l1c
from common.io.readGeodetic import readGeodetic
from common.io.writeToa import readToa

# PLOT 1 COMPARATIVO L1C VS L1B

# =========================================================
# DIRECTORIES
# =========================================================

auxdir = r'C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\EODT_Mario\\auxiliary'
# GM dir + L1B dir
indir = r'C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1C\input\gm_alt100_act_150\,C:\Users\mbell\OneDrive\Escritorio\EODT\SHARED\EODP_TER_2021\EODP-TS-L1C\input\l1b_output'
outdir = r'C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\SHARED\\EODP_TER_2021\\EODP-TS-L1C\\output_Mario'

# =========================================================
# INITIALISE L1C
# =========================================================

myL1c = l1c(auxdir, indir, outdir)

# =========================================================
# READ L1B DATA
# =========================================================

band = myL1c.globalConfig.bands[0]

toa = myL1c.globalConfig.l1b_toa + band + '.nc'

# Radiances
from common.io.writeToa import readToa
toa = readToa(myL1c.l1bdir, toa)

# Geolocation
lat, lon = readGeodetic(
    myL1c.gmdir,
    myL1c.globalConfig.gm_geoloc
)


# =========================================================
# L1C REPROJECTION
# =========================================================

lat_l1c, lon_l1c, toa_l1c = myL1c.l1cProjtoa(
    lat,
    lon,
    toa,
    band
)


# =========================================================
# PLOT
# =========================================================

plt.figure(figsize=(10, 7))


# -------------------------
# L1B - BLUE POINTS
# -------------------------

plt.scatter(
    lon,
    lat,
    color='red',
    s=8,
    label='L1B'
)


# -------------------------
# L1C - RED POINTS
# -------------------------

plt.scatter(
    lon_l1c,
    lat_l1c,
    color='blue',
    s=8,
    label='L1C'
)


# -------------------------
# FORMAT
# -------------------------

plt.xlabel('Longitude [deg]')
plt.ylabel('Latitude [deg]')
plt.title('L1B vs L1C grid')

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()




# =========================================================
# PLOT 2: L1B SPATIAL SAMPLING DISTANCE
# =========================================================

line = 50

lat_line = lat[line, :]
lon_line = lon[line, :]


# Earth's radius [m]
R = 6371000


# Convert degrees to radians
lat_rad = np.radians(lat_line)
lon_rad = np.radians(lon_line)


# Differences between consecutive samples
dlat = np.diff(lat_rad)
dlon = np.diff(lon_rad)


# =========================================================
# HAVERSINE DISTANCE
# =========================================================

a = (
    np.sin(dlat / 2) ** 2
    + np.cos(lat_rad[:-1])
    * np.cos(lat_rad[1:])
    * np.sin(dlon / 2) ** 2
)

distance = 2 * R * np.arcsin(np.sqrt(a))


# =========================================================
# PRINT RESULTS
# =========================================================

print('--------------------------------------------')
print('L1B SPATIAL SAMPLING DISTANCE')
print('--------------------------------------------')

print('Line:', line)
print('Number of L1B samples:', len(lat_line))
print('Number of distances:', len(distance))

print('Minimum distance [m]:', np.min(distance))
print('Maximum distance [m]:', np.max(distance))
print('Mean distance [m]:', np.mean(distance))

# =========================================================
# PLOT
# =========================================================

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

# =========================================================
# PLOT 3: L1B SPATIAL SAMPLING DISTANCE - COLUMN 75
# =========================================================

column = 75

lat_column = lat[:, column]
lon_column = lon[:, column]


# Convert degrees to radians
lat_rad = np.radians(lat_column)
lon_rad = np.radians(lon_column)


# Differences between consecutive samples
dlat = np.diff(lat_rad)
dlon = np.diff(lon_rad)


# =========================================================
# HAVERSINE DISTANCE
# =========================================================

a = (
    np.sin(dlat / 2) ** 2
    + np.cos(lat_rad[:-1])
    * np.cos(lat_rad[1:])
    * np.sin(dlon / 2) ** 2
)

distance_column = 2 * R * np.arcsin(np.sqrt(a))


# =========================================================
# PRINT RESULTS
# =========================================================

print('--------------------------------------------')
print('L1B SPATIAL SAMPLING DISTANCE - COLUMN')
print('--------------------------------------------')

print('Column:', column)
print('Number of L1B samples:', len(lat_column))
print('Number of distances:', len(distance_column))

print('Minimum distance [m]:', np.min(distance_column))
print('Maximum distance [m]:', np.max(distance_column))
print('Mean distance [m]:', np.mean(distance_column))


# =========================================================
# PLOT
# =========================================================

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
