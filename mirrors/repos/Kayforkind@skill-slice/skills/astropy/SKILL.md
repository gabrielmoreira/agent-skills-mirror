---
name: astropy
description: "Runs the astropy Python stack for SkyCoord frame transforms, FITS read/write, unit Quantities, Planck18 distances, and Time scale conversions. Use for ICRS/Galactic/AltAz, WCS pixel-world, or FITS catalog work. Not a general NumPy/SciPy notebook skill without astronomical frames or FITS."
version: 1.0.1
license: BSD-3-Clause
metadata:
  skill-author: K-Dense Inc.
risk: unknown
source: "https://github.com/astropy/astropy"
---

# Astropy

## Overview

Astropy is the core Python package for astronomy, providing essential functionality for astronomical research and data analysis. Use astropy for coordinate transformations, unit and quantity calculations, FITS file operations, cosmological calculations, precise time handling, tabular data manipulation, and astronomical image processing.

## When to Use

Trigger this skill when the task involves any of the following:

- Converting between celestial coordinate systems (ICRS, Galactic, FK5, AltAz, etc.)
- Working with physical units and quantities (converting Jy to mJy, parsecs to km, etc.)
- Reading, writing, or manipulating FITS files (images or tables)
- Cosmological calculations (luminosity distance, lookback time, Hubble parameter)
- Precise time handling with different time scales (UTC, TAI, TT, TDB) and formats (JD, MJD, ISO)
- Table operations (reading catalogs, cross-matching, filtering, joining)
- WCS transformations between pixel and world coordinates
- Astronomical constants and calculations

## Prerequisites

1. **Python 3.9+** installed on the system.
2. **uv** package manager available (preferred) or pip.
3. On Windows (primary host), use PowerShell. Paths use backslashes (`~`).
4. Astropy installed in the active environment:

```powershell
uv pip install astropy
# Or with optional dependencies for full functionality:
uv pip install astropy[all]
```

5. For FITS I/O, image display, or HDF5 table support, ensure optional dependencies (`numpy`, `matplotlib`, `h5py`) are installed.

## Procedure

### Step 1 — Identify the Astropy Subsystem Needed

Match the task to the correct module before writing code:

| Task | Module | Reference File to Load |
|------|--------|----------------------|
| Unit conversion, quantities | `astropy.units` | `references/units.md` |
| Coordinate transforms, catalog matching | `astropy.coordinates` | `references/coordinates.md` |
| Cosmological distances, ages | `astropy.cosmology` | `references/cosmology.md` |
| FITS file read/write | `astropy.io.fits` | `references/fits.md` |
| Table I/O, joins, filtering | `astropy.table` | `references/tables.md` |
| Time scales, formats, arithmetic | `astropy.time` | `references/time.md` |
| WCS, NDData, modeling, visualization, constants, convolution, stats | `astropy.wcs` and others | `references/wcs_and_other_modules.md` |

**Progressive disclosure rule:** Load the specific `references/<module>.md` file only when the task requires detail beyond the quick-start examples below. Do not load all reference files at once.

### Step 2 — Quick Start: Core Imports

```python
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.io import fits
from astropy.table import Table
from astropy.cosmology import Planck18
```

### Step 3 — Units and Quantities

```python
import astropy.units as u

distance = 100 * u.pc
distance_km = distance.to(u.km)

# Equivalencies for spectral conversions
frequency = 1.4 * u.GHz
wavelength = frequency.to(u.cm, equivalencies=u.spectral())
```

Load `references/units.md` when you need: logarithmic units (magnitudes), custom equivalencies, Doppler conversions, performance optimization for large arrays, or unit arithmetic edge cases.

### Step 4 — Coordinate Transformations

```python
from astropy.coordinates import SkyCoord
import astropy.units as u

c = SkyCoord(ra='05h23m34.5s', dec='-69d45m22s', frame='icrs')
c_gal = c.galactic
print(f"l={c_gal.l.deg}, b={c_gal.b.deg}")

# AltAz transform requires time and location
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz

observing_time = Time('2023-06-15 23:00:00')
observing_location = EarthLocation(lat=40*u.deg, lon=-120*u.deg)
aa_frame = AltAz(obstime=observing_time, location=observing_location)
c_altaz = c.transform_to(aa_frame)
print(f"Alt={c_altaz.alt.deg}, Az={c_altaz.az.deg}")
```

Load `references/coordinates.md` when you need: frame definitions, proper motion handling, radial velocities, 3D coordinates with distance, observer-dependent frame details, or catalog cross-matching performance tips.

### Step 5 — FITS File Handling

```python
from astropy.io import fits
import numpy as np

with fits.open('observation.fits') as hdul:
    hdul.info()
    data = hdul[1].data
    header = hdul[1].header
    exptime = header['EXPTIME']
    filter_name = header['FILTER']
    mean = np.mean(data)
    median = np.median(data)
    print(f"Mean: {mean}, Median: {median}")
```

Load `references/fits.md` when you need: multi-extension FITS creation, header manipulation (comments, history), memory mapping for large files, binary vs ASCII table handling, or remote FITS access (S3, HTTP).

### Step 6 — Table Operations

```python
from astropy.table import Table

table = Table.read('catalog.fits')
# Filter
filtered = table[table['FLUX'] > 1e-15]
# Write
filtered.write('filtered_catalog.csv', format='csv', overwrite=True)
```

Load `references/tables.md` when you need: QTable for unit-aware columns, joins, grouping, aggregation, stacking, masking, or multi-format I/O (HDF5, VOTable).

### Step 7 — Time Handling

```python
from astropy.time import Time

t = Time('2023-01-15 12:30:00')
jd = t.jd  # Julian Date
mjd = t.mjd  # Modified Julian Date

# Time scale conversion
t_tdb = t.tdb
print(f"UTC: {t.utc.iso}, TDB: {t_tdb.iso}")
```

Load `references/time.md` when you need: sidereal time calculations, light travel time corrections (barycentric, heliocentric), time arrays, masked times, or precision handling beyond microsecond level.

### Step 8 — Cosmological Calculations

```python
from astropy.cosmology import Planck18
import astropy.units as u

z = 1.5
d_L = Planck18.luminosity_distance(z)
d_A = Planck18.angular_diameter_distance(z)
age = Planck18.age(z)
t_lookback = Planck18.lookback_time(z)

print(f"Luminosity distance: {d_L}")
print(f"Angular diameter distance: {d_A}")
print(f"Age at z={z}: {age.to(u.Gyr)}")
print(f"Lookback time: {t_lookback.to(u.Gyr)}")
```

Load `references/cosmology.md` when you need: custom cosmological models, inverse calculations (find z for given distance), density parameters, neutrino effects, or comparison of built-in cosmologies (Planck18, WMAP9, etc.).

### Step 9 — WCS and Other Modules

```python
from astropy.wcs import WCS

with fits.open('image.fits') as hdul:
    header = hdul[0].header
    wcs = WCS(header)
    # Pixel to world
    ra, dec = wcs.all_pix2world(100, 200, 0)
    print(f"RA={ra}, Dec={dec}")
```

Load `references/wcs_and_other_modules.md` when you need: WCS creation, footprint calculations, NDData/CCDData containers, model fitting, visualization with stretching/scaling, constants with units, convolution kernels, or robust statistics (sigma clipping).

## Examples

### Cross-Matching Catalogs

```python
from astropy.table import Table
from astropy.coordinates import SkyCoord
import astropy.units as u

cat1 = Table.read('catalog1.fits')
cat2 = Table.read('catalog2.fits')

coords1 = SkyCoord(ra=cat1['RA']*u.degree, dec=cat1['DEC']*u.degree)
coords2 = SkyCoord(ra=cat2['RA']*u.degree, dec=cat2['DEC']*u.degree)

idx, sep, _ = coords1.match_to_catalog_sky(coords2)

max_sep = 1 * u.arcsec
matches = sep < max_sep
cat1_matched = cat1[matches]
cat2_matched = cat2[idx[matches]]
print(f"Found {len(cat1_matched)} matches")
```

### Cosmological Distance at Multiple Redshifts

```python
from astropy.cosmology import Planck18
import astropy.units as u
import numpy as np

redshifts = np.linspace(0.01, 5.0, 50)
d_L = Planck18.luminosity_distance(redshifts)
print(d_L[:5])
```

## Pitfalls

1. **Missing units on raw numbers**: Always attach units (`100 * u.pc`). Bare floats passed to astropy functions expecting Quantities will raise `UnitsError`.
2. **FITS files left open**: Always use `with fits.open(...) as hdul:` context manager. Failing to close FITS files can cause file locking on Windows.
3. **Coordinate frame assumptions**: `SkyCoord` defaults to ICRS. If the data is in FK5 or Galactic, specify `frame=` explicitly or transformations will be wrong.
4. **AltAz without obstime/location**: `AltAz` frame requires both `obstime` and `location`. Omitting either raises an error.
5. **Time scale confusion**: `Time('2023-01-15 12:30:00')` defaults to UTC. For TDB or TT calculations, explicitly set `scale='tdb'` or convert with `.tdb`.
6. **Cosmology mismatch**: Using `WMAP9` when the analysis expects `Planck18` (or vice versa) produces different distances. Always state which cosmology is used.
7. **Looping over coordinates**: Processing one coordinate at a time in a Python loop is slow. Pass arrays to `SkyCoord` for vectorized operations.
8. **WCS from wrong HDU**: WCS keywords may be in the primary header (`hdul[0]`) or an extension header (`hdul[1]`). Check `hdul.info()` first.
9. **Table column units lost on write**: Some formats (CSV) do not preserve units. Use FITS or VOTable to retain unit metadata, or use `QTable`.
10. **Memory mapping on Windows**: `fits.open(..., memmap=True)` can cause issues if the file is also open in another application. Close all handles before reopening.
11. **Do not treat skill output as a substitute** for environment-specific validation, testing, or expert review.
12. **Stop and ask for clarification** if required inputs, permissions, safety boundaries, or success criteria are missing.

## Verification

Run these checks to confirm astropy is installed and functional:

```powershell
# Check installation
python -c "import astropy; print(astropy.__version__)"
```

Expected output: a version string (e.g., `6.1.x` or newer).

```powershell
# Verify units module
python -c "import astropy.units as u; print((100 * u.pc).to(u.km))"
```

Expected output: a Quantity in km (e.g., `3.0856775814671917e+15 km`).

```powershell
# Verify coordinates
python -c "from astropy.coordinates import SkyCoord; import astropy.units as u; c = SkyCoord(ra=10.5*u.degree, dec=41.2*u.degree, frame='icrs'); print(c.galactic)"
```

Expected output: Galactic coordinates `<SkyCoord (Galactic): l=..., b=... deg>`.

```powershell
# Verify cosmology
python -c "from astropy.cosmology import Planck18; print(Planck18.luminosity_distance(1.0))"
```

Expected output: a Quantity (e.g., `6608.76 Mpc`).

```powershell
# Verify FITS I/O (round-trip)
python -c "from astropy.io import fits; import numpy as np; hdu = fits.PrimaryHDU(np.arange(10)); hdu.writeto('test_verify.fits', overwrite=True); d = fits.getdata('test_verify.fits'); print(d)"
```

Expected output: `array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])`.

## Related Skills

- **numpy** — Array operations underlying astropy data structures
- **matplotlib** — Plotting astropy quantities and images
- **scipy** — Scientific computing complement to astropy modeling and stats

## Reference Files

Load these on demand (progressive disclosure) — do not load all at once:

- `references/units.md` — Units, quantities, conversions, equivalencies, logarithmic units, performance
- `references/coordinates.md` — Coordinate frames, transformations, catalog matching, proper motions, AltAz
- `references/cosmology.md` — Cosmological models, distances, ages, inverse calculations, neutrino effects
- `references/fits.md` — FITS file operations, header manipulation, memory mapping, multi-extension, remote access
- `references/tables.md` — Table creation, I/O, joins, grouping, QTable, masking, multi-format support
- `references/time.md` — Time formats, scales, arithmetic, sidereal time, light travel time, precision
- `references/wcs_and_other_modules.md` — WCS, NDData, CCDData, modeling, visualization, constants, convolution, statistics

## Documentation and Resources

- Official Astropy Documentation: https://docs.astropy.org/en/stable/
- Tutorials: https://learn.astropy.org/
- GitHub: https://github.com/astropy/astropy
