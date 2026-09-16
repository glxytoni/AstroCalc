# 🌌 AstroCalc

AstroCalc is a Python desktop application for astronomy, astrophysics, orbital mechanics, and spaceflight calculations. It provides practical, physically based tools through a tabbed Tkinter interface.

> AstroCalc is intended for education, exploration, and approximate analysis. It is not a mission-planning or high-precision ephemeris tool.

## Features

### Physics & Relativity

- Relativistic kinetic-energy calculator
- Particle mass-energy calculator
- Photon energy and electromagnetic-spectrum calculator
- Schwarzschild-radius calculator

### Orbits & Spaceflight

- Hohmann transfer ΔV calculator with orbit visualisation
- Two-body orbit visualizer for Earth and Sun
  - apoapsis/periapsis input mode
  - periapsis-velocity input mode
  - elliptic, parabolic, and hyperbolic trajectories
  - optional Earth-Moon and Solar System reference orbits
- Multi-stage rocket ΔV and burn-time calculator
- Roche-limit calculator

### Stellar Astronomy

- Stellar magnitude calculator
- Stellar spectral-class and peak-wavelength calculator
- Parallax-distance calculator

### Cosmology

- Redshift-distance calculator using the Astropy `Planck15` cosmology model

## Interface

AstroCalc opens to a dashboard with four calculator categories:

- Physics & Relativity
- Orbits & Spaceflight
- Stellar Astronomy
- Cosmology

Calculators open in tabs within the same application window. Selecting an already-open calculator focuses its existing tab, and each calculator tab can be closed individually.

## Requirements

- Python 3.10 or newer recommended
- Tkinter
- SciPy
- Astropy

Install the external dependencies:

```powershell
python -m pip install scipy astropy
```

Tkinter is normally included with standard Python installations on Windows.

## Running AstroCalc

From the project folder:

```powershell
python ACmain.py
```

## Project structure

```text
AstroCalc/
├── ACmain.py   # Application launcher, dashboard, menus, and tab management
├── aclib.py    # Calculator logic, visualisation helpers, and UI builders
└── README.md
```

## Notes on models and units

- Inputs and outputs use SI units unless a field explicitly states another unit.
- Hohmann transfers assume ideal, coplanar circular orbits.
- The Orbit Visualizer uses an ideal two-body Keplerian model.
- Redshift distance is based on the Planck15 cosmology model.
- Results are approximate and depend on the assumptions of each calculator.

## Planned tools

The interface includes placeholders for future features, including:

- Relativistic speed / kinetic-energy analysis
- Patched-conics gravity-assist visualizer
- Orbit analysis
- Stellar-distance estimation
- Stellar constants and additional stellar tools

## License

No license has been specified yet.
