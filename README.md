# 🌌 AstroCalc 0.4.0 — UI 2.0

A desktop calculator for astronomy, physics, orbital mechanics, and spaceflight. Explore everything from photon energies to multi-stage rockets through a tabbed Tkinter interface.

Version **0.4.0** brings the available calculators into **UI 2.0**: consistent input and result sections, readable answers, scrollable layouts, and expandable details.

> Built for education, experimentation, and approximate analysis—not operational mission planning or flight-critical decisions.

## What's new in 0.4.0

- A four-category dashboard with calculators opening in reusable tabs.
- Bold primary results, Calculate/Reset controls, and details or conversion panels where applicable.
- Closing a calculator selects the next calculator tab, then the previous one, before returning to the dashboard.
- Zoom, pan, and fit controls for orbit and Hohmann-transfer diagrams.
- A redshift-distance diagram showing distance today relative to our observable universe.
- A rebuilt rocket calculator with payload, dynamic stages, engine counts, and estimated-ascent performance.
- A Windows executable build with a custom AstroCalc icon.

## Calculators

### Physics & Relativity

- **Relativistic Kinetic Energy:** energy from mass and velocity, entered in m/s or as a fraction of light speed.
- **Mass-Energy Calculator:** particle presets, velocity-to-energy and total-energy-to-velocity modes.
- **Photon Energy / Spectrum:** photon energy and electromagnetic-spectrum classification from wavelength.
- **Schwarzschild Radius:** black-hole radius from mass, with multiple output units.

The relativity and mass-energy tools prioritise conversions with magnitudes from 0.001 to below 1000, with a base-unit fallback. **Show all conversions** keeps the full set available.

### Orbits & Spaceflight

- **Orbit Visualizer:** Earth/Sun two-body trajectories from apoapsis/periapsis or velocity at periapsis; elliptic, parabolic, and hyperbolic cases, reference orbits, and detailed results.
- **Hohmann Transfer:** departure/arrival burns, total ΔV, transfer time, burn directions, and the highlighted transfer arc.
- **Roche Limit:** fluid and rigid estimates, using radius in km and densities in g/cm³. Distances are measured from the primary body's centre.
- **Rocket DeltaV:** sequential multi-stage ΔV, propellant masses, burn times, and thrust-to-weight ratios.

Use the mouse wheel to zoom orbital diagrams, drag to pan, and **Fit orbit** to restore the view.

### Stellar Astronomy

- **Stellar Magnitude:** apparent/absolute magnitude calculations.
- **Stellar Spectrum:** temperature-based spectral classification and peak wavelength.
- **Parallax Distance:** distance from stellar parallax.

### Cosmology

- **Hubble Expansion via Redshift:** present-day proper distance, light-travel time, and additional distance conversions using Astropy's `Planck15` cosmology.
- A flat, observer-centred circle with the Milky Way at its centre and a right-pointing distance arrow, labelled with redshift and light-years.
- The observable radius is calculated from the same cosmological model, approximately **46.27 billion light-years**.

The circle is a schematic of our observable region, not the physical edge of the entire universe. The arrow's direction is illustrative; distance today is not light-travel time multiplied by light speed.

## Rocket calculator guide

### Masses and staging

1. Enter stages **bottom to top**. Stage 1 burns first.
2. Enter each stage's **own wet and dry masses**, in tonnes. Exclude payload and all other stages.
3. Enter payload separately; it remains aboard throughout the calculation.
4. Use **Add stage** and **Remove** to change the stack.

Wet mass includes propellant; dry mass includes the empty tanks, engines, and structure. Upper-stage mass and payload are added automatically during each burn. Spent dry stage mass is discarded before the next stage fires.

### Engines and conditions

- Thrust is optional: masses and Isp are enough for ideal ΔV. Burn time and TWR require thrust.
- Supported engine presets fill Isp and total thrust using **1–30 engines per stage**. Isp does not multiply with engine count.
- F-1, RS-25, and Merlin 1D provide both sea-level and vacuum reference values. J-2 and RL10B-2 provide vacuum values only.
- Raptor and generic Isp presets remain Isp-only; matching thrust must be entered manually.
- Editing preset performance switches to **Custom**. Custom thrust is the total stage thrust in kN.
- Engine mass is **not** added automatically: include it in both wet and dry stage masses.

Each stage has three performance modes:

| Mode | Meaning |
| --- | --- |
| Atmosphere | Fixed sea-level thrust and Isp; the initial default for stage 1. |
| Vacuum | Fixed vacuum thrust and Isp; the initial default for later stages. |
| Estimated ascent | An adjustable blend between both endpoints, initially 50%. Requires a preset with both references. |

Estimated ascent shows sea-level, vacuum, and used values. A 50% blend is a **midpoint assumption**, not a measured ascent average or a percentage of burn time spent in vacuum. Stage 1 liftoff TWR still uses sea-level thrust in this mode.

Results include total and per-stage ΔV, a coloured contribution bar, propellant mass, and available burn-time/TWR figures. All TWR values use Earth standard gravity. The optional Earth-liftoff check applies to stage 1; low upper-stage TWR is not automatically a failure.

### Model limits

The rocket model assumes sequential burns with constant performance during each burn. It does **not** simulate trajectory, atmospheric drag, gravity or steering losses, throttle schedules, parallel boosters, crossfeed, or coast time. Estimated ascent remains an idealised approximation—not a launch simulation.

The other orbital tools also use idealised models: two-body Keplerian motion for the Orbit Visualizer and coplanar circular starting/target orbits for Hohmann transfers. Always follow the units shown beside each input.

## Run from source

Requirements: Python 3.10 or newer with Tkinter, plus SciPy and Astropy. Tkinter is normally included with the standard Windows Python installer.

From the project folder in PowerShell, using a standard Windows Python installation:

```powershell
py -3 -m venv .venv-exe
.\.venv-exe\Scripts\python.exe -m pip install scipy astropy
.\.venv-exe\Scripts\python.exe ACmain.py
```

If the `py` launcher is unavailable, replace `py -3` with the full path to your standard Python executable. Reusing the same `.venv-exe` folder does not create additional environments.

## Build a Windows executable

Use a clean environment based on standard Windows Python for packaging. A virtual environment created from Anaconda caused missing Tcl/Tk DLLs in the tested build; it is not the recommended packaging setup.

With the environment above created and `astrocalc.ico` in the project folder:

```powershell
.\.venv-exe\Scripts\python.exe -m pip install pyinstaller
.\.venv-exe\Scripts\python.exe -m PyInstaller --clean --onefile --windowed --name "Astrocalc 0.4.0" --icon "astrocalc.ico" ACmain.py
```

Output: **`dist\Astrocalc 0.4.0.exe`**

- `aclib.py` and detected dependencies are bundled automatically; recipients do not need Python installed.
- Close any running copy before rebuilding. Source changes require a new build.
- Keep `--icon` in future build commands to retain the executable icon.
- A one-file build can take a little longer to start because dependencies are extracted at launch.
- Test the packaged calculators before sharing. For startup problems, rebuild without `--windowed` and run from PowerShell to see diagnostic output.

See the [PyInstaller documentation](https://pyinstaller.org/en/stable/usage.html) for additional build options.

## Project structure

```text
AstroCalc/
├── ACmain.py      # Launcher, dashboard, menus, and tab management
├── aclib.py       # Calculations, visualisations, and calculator interfaces
├── astrocalc.ico  # Windows executable icon
└── README.md
```

`.venv-exe/`, `build/`, `dist/`, and generated `.spec` files are local environment/build files, not calculator source files.

## Not yet implemented

Menu entries marked **Coming soon** or **WIP** are placeholders, including patched-conics gravity assists, a separate orbit-analysis tool, additional relativistic speed/energy tools, stellar-distance estimation, and stellar constants.

## License

No license has been specified yet.
