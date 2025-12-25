import math
import ast
import tkinter as tk
from tkinter import ttk
from tkinter import font


solarradius = 6.69e8  # meter
solarmass = 1.988e30  # kg
gravsun = 274  # m/s**2
solarconstant = 1367  # Watt/m**2
solarlum = 3.828e26 #W

radiusearth = 6.378e6  # meter
massearth = 5.9722e24  # kg
gravearth = 9.81  # m/s**2
numexce = 0.0167

G = 6.6741e-11
pi = math.pi
AU = 149597870700  # meter
c = 2.9979e8  # meter
ly = 9.461e15  # meter
psc = 3.086e16  # meter
h = 6.626e-34  # Js = 4.1357e-15 eVs
theta = 5.6704e-8  # Stefan-Boltzmann
bW = 2.8978e-3
eV = 1.602176634e-19  # 1 eV in Joules
H01 = 72
H02 = 67

SOLAR_SYSTEM = {
"""
    "constants": {
        "G":            6.6741e-11,      # gravitational constant (m^3 / kg / s^2)
        "pi":           3.141592653589793,
        "AU":           1.495978707e11,  # meter
        "c":            2.9979e8,        # m/s
        "ly":           9.461e15,        # meter
        "parsec":       3.086e16,        # meter
        "h":            6.626e-34,       # J*s
        "sigma":        5.6704e-8,       # Stefan-Boltzmann (W/m^2/K^4)
        "bWien":        2.8978e-3,       # Wien displacement constant (m*K)

        # Hubble parameter examples you had
        "H01":          72,
        "H02":          67
    },
"""
    "sun": {
        "radius":       6.69e8,          # meter
        "mass":         1.988e30,        # kg
        "gravity":      274,             # m/s^2 at surface
        "solar_constant": 1367,          # W/m^2 at 1 AU
        "luminosity":   3.828e26         # W
    },

    # --- Planets ---
    "mercury": {
        "radius":       2.4397e6,        # m
        "mass":         3.3011e23,       # kg
        "gravity":      3.7              # m/s^2
    },

    "venus": {
        "radius":       6.0518e6,        # m
        "mass":         4.8675e24,       # kg
        "gravity":      8.87             # m/s^2
    },

    "earth": {
        "radius":       6.371e6,         # m
        "mass":         5.9722e24,       # kg
        "gravity":      9.80665,         # m/s^2
        "eccentricity": 0.0167           # mean orbital eccentricity (you already had this)
    },

    "mars": {
        "radius":       3.3895e6,        # m
        "mass":         6.4171e23,       # kg
        "gravity":      3.72076          # m/s^2
    },

    "jupiter": {
        "radius":       6.9911e7,        # m
        "mass":         1.8982e27,       # kg
        "gravity":      24.79            # m/s^2
    },

    "saturn": {
        "radius":       5.8232e7,        # m
        "mass":         5.6834e26,       # kg
        "gravity":      10.44            # m/s^2
    },

    "uranus": {
        "radius":       2.5362e7,        # m
        "mass":         8.6810e25,       # kg
        "gravity":      8.69             # m/s^2
    },

    "neptune": {
        "radius":       2.4622e7,        # m
        "mass":         1.02413e26,      # kg
        "gravity":      11.15            # m/s^2
    }
}

#=====  Backend shi ===========================================

def draw_central_body(canvas, cx, cy, body_radius_m,  scale, color, min_px=4, max_px=160):

    """
       Draw central body with physically-scaled radius,
       clamped to remain visible.
       """

    r_px = body_radius_m * scale

    # Clamp for usability
    r_px = max(min_px, min(max_px, r_px))

    canvas.create_oval(
        cx - r_px, cy - r_px,
        cx + r_px, cy + r_px,
        fill=color,
        outline=""
    )


def compute_orbit_scale(canvas_size, radii, padding=30):
    max_r = max(radii)
    return (canvas_size / 2 - padding) / max_r


"""
def draw_kepler_orbit_disabled(canvas, a, e, scale, cx, cy,
                      color="white", width=2, dashed=False):

    if a <= 0 or e >= 1:
        return

    b = a * math.sqrt(1 - e**2)
    c = a * e

    x0 = cx - (a - c) * scale
    y0 = cy - b * scale
    x1 = cx + (a + c) * scale
    y1 = cy + b * scale

    canvas.create_oval(
        x0, y0, x1, y1,
        outline=color,
        width=width,
        dash=(4, 4) if dashed else None
    )
"""


def draw_kepler_orbit(canvas, a, e, scale, cx, cy,
                      color="white", width=2):
    """
    Draws an elliptical or hyperbolic Kepler orbit.
    Focus is at the central body (cx, cy).
    """

    points = []

    # --- Angle range ---
    if e < 1.0:
        # Ellipse
        theta_min = 0.0
        theta_max = 2 * math.pi
        steps = 600
    else:
        # Hyperbola: limit to real values
        theta_max = math.acos(-1 / e)
        theta_min = -theta_max
        steps = 600

    dtheta = (theta_max - theta_min) / steps

    theta = theta_min
    for _ in range(steps + 1):
        denom = 1 + e * math.cos(theta)

        # Skip invalid regions
        if denom > 0:
            r = a * (1 - e**2) / denom

            if r > 0:
                x = cx + r * math.cos(theta) * scale
                y = cy - r * math.sin(theta) * scale
                points.extend([x, y])

        theta += dtheta

    if len(points) > 4:
        canvas.create_line(
            points,
            fill=color,
            width=width,
            smooth=True,
            dash=(6, 4) if e > 1 else None
        )

def draw_reference_orbits(canvas, mode, scale, cx, cy):
    AU = 1.495978707e11
    moon_orbit = 384_400_000

    solar_orbits = [
        0.387 * AU,
        0.723 * AU,
        1.000 * AU,
        1.524 * AU,
        5.203 * AU,
        9.537 * AU,
        19.191 * AU,
        30.070 * AU,
    ]

    if mode == "solar":
        for r in solar_orbits:
            canvas.create_oval(
                cx - r * scale,
                cy - r * scale,
                cx + r * scale,
                cy + r * scale,
                outline="#555555",
                dash=(3, 3)
            )

    elif mode == "earth_moon":
        canvas.create_oval(
            cx - moon_orbit * scale,
            cy - moon_orbit * scale,
            cx + moon_orbit * scale,
            cy + moon_orbit * scale,
            outline="#555555",
            dash=(3, 3)
        )

#====================================================================================


def hohmann_transfer_UI3(root):
    import tkinter as tk
    import math

    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    bodies = {
        "Earth": (3.986004418e14, 6.371e6),
        "Moon": (4.9048695e12, 1.7374e6),
        "Mars": (4.282837e13, 3.3895e6),
        "Venus": (3.24859e14, 6.0518e6),
        "Sun": (1.32712440018e20, 6.9634e8),
    }

    selected_body = tk.StringVar(value="Earth")

    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    body_frame = tk.Frame(frame)
    body_frame.pack(anchor="w")

    tk.Label(body_frame, text="Central body: ").pack(side=tk.LEFT)
    tk.OptionMenu(body_frame, selected_body, *bodies.keys()).pack(side=tk.LEFT)

    input_frame = tk.Frame(frame)
    input_frame.pack(anchor="w", pady=10)

    labels = [
        "Start Orbit Altitude [km]: ",
        "Final Orbit Altitude [km]: "
    ]

    entries = []
    for text in labels:
        row = tk.Frame(input_frame)
        row.pack(anchor="w", pady=4)
        tk.Label(row, text=text).pack(side=tk.LEFT)
        e = tk.Entry(row, width=16)
        e.pack(side=tk.LEFT)
        entries.append(e)

    start_alt_entry, final_alt_entry = entries

    CANVAS_SIZE = 420
    canvas = tk.Canvas(frame, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="black")
    canvas.pack(pady=10)

    result_label = tk.Label(frame, justify=tk.LEFT, anchor="w")
    result_label.pack(fill=tk.X, pady=6)

    def calculate():
        try:
            h1 = float(start_alt_entry.get()) * 1000  # start altitude [m]
            h2 = float(final_alt_entry.get()) * 1000  # final altitude [m]
        except ValueError:
            result_label.config(text="Error: Invalid input, please enter numeric altitudes in km.")
            return

        if h1 < 0 or h2 < 0:
            result_label.config(text="Error: Altitudes must be >= 0.")
            return

        mu, R = bodies[selected_body.get()]

        # --- Radii from central body ---
        r1 = R + h1
        r2 = R + h2

        # --- Circular velocities ---
        v1 = math.sqrt(mu / r1)
        v2 = math.sqrt(mu / r2)

        # --- Transfer orbit ---
        a_t = (r1 + r2) / 2.0
        vtp = math.sqrt(mu * (2.0 / r1 - 1.0 / a_t))
        vta = math.sqrt(mu * (2.0 / r2 - 1.0 / a_t))

        # --- Burns ---
        dv1 = abs(vtp - v1)
        dv2 = abs(v2 - vta)

        result_label.config(text=(
            f"Hohmann Transfer ({selected_body.get()}):\n"
            f"ΔV₁ = {dv1 / 1000:.6f} km/s\n"
            f"ΔV₂ = {dv2 / 1000:.6f} km/s\n"
            f"Total ΔV = {(dv1 + dv2) / 1000:.6f} km/s"
        ))

        # ---- DRAWING ----
        canvas.delete("all")
        cx = cy = CANVAS_SIZE / 2

        # Scale based on *largest orbit actually drawn*
        scale = compute_orbit_scale(
            CANVAS_SIZE,
            [r1, r2, a_t * (1 + abs(r2 - r1) / (r2 + r1))]
        )

        mode = "solar" if selected_body.get() == "Sun" else "earth_moon"

        # Pick color based on central body
        body_color = "yellow" if mode == "solar" else "blue"

        # Central body (NEW signature)
        draw_central_body(
            canvas,
            cx,
            cy,
            R,  # physical radius in meters
            scale,
            "blue"
        )

        # Reference orbits
        draw_reference_orbits(canvas, mode, scale, cx, cy)


        # --- Start orbit (circular) ---
        a1 = r1  # semi-major axis = radius
        e1 = 0.0  # circular
        draw_kepler_orbit(canvas, a1, e1, scale, cx, cy)

        # --- Transfer orbit (elliptical) ---
        a_t = (r1 + r2) / 2.0
        e_t = abs(r2 - r1) / (r2 + r1)
        draw_kepler_orbit(canvas, a_t, e_t, scale, cx, cy)

        # --- Final orbit (circular) ---
        a2 = r2
        e2 = 0.0
        draw_kepler_orbit(canvas, a2, e2, scale, cx, cy)

    tk.Button(frame, text="Calculate ΔV", command=calculate).pack(pady=8)
    start_alt_entry.focus()



def orbit_visualizer_UI2(root):
    # -----------------------------
    # Clear existing UI
    # -----------------------------
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    AU_KM = 149_597_870

    # -----------------------------
    # State
    # -----------------------------
    system_mode = tk.StringVar(value="Solar System")

    # -----------------------------
    # Inner draw function
    # -----------------------------
    def draw_orbit():
        try:
            ra_input = float(apo_entry.get())
            rp_input = float(peri_entry.get())
        except ValueError:
            info_label.config(text="Error: Invalid input.")
            return

        # Convert units to km
        if system_mode.get() == "Solar System":
            ra = ra_input * AU_KM
            rp = rp_input * AU_KM
        else:
            ra = ra_input
            rp = rp_input

        if rp <= 0 or ra <= 0 or ra < rp:
            info_label.config(text="Error: Require ra ≥ rp > 0")
            return

        canvas.delete("all")

        # --- Orbital geometry ---
        a = (ra + rp) / 2
        e = (ra - rp) / (ra + rp)
        b = a * math.sqrt(1 - e**2)
        c = a * e

        # --- Scaling (always scale to analyzed orbit) ---
        padding = 40
        scale = (CANVAS_SIZE / 2 - padding) / ra

        cx = CANVAS_SIZE / 2
        cy = CANVAS_SIZE / 2

        # -----------------------------
        # System definitions
        # -----------------------------
        if system_mode.get() == "Solar System":
            central_color = "yellow"
            reference_orbits = [
                ("Mercury",  57_909_227,  "#808080"),
                ("Venus",   108_209_475,  "#FFFFF0"),
                ("Earth",   149_597_870,  "#3399ff"),
                ("Mars",    227_943_824,  "#ff3333"),
                ("Jupiter", 778_340_821,  "#ff8c00"),
                ("Saturn", 1_426_666_422, "#ffa500"),
                ("Uranus", 2_870_658_186, "#66ccff"),
                ("Neptune",4_498_396_441, "#00008b"),
            ]
        else:
            central_color = "#3399ff"  # Earth
            reference_orbits = [
                ("Moon", 384_400, "#cccccc")
            ]

        # -----------------------------
        # Central body
        # -----------------------------
        focus_x = cx - c * scale
        focus_y = cy

        canvas.create_oval(
            focus_x - 5, focus_y - 5,
            focus_x + 5, focus_y + 5,
            fill=central_color,
            outline=""
        )

        # -----------------------------
        # Reference orbits
        # -----------------------------
        for _, orbit_km, color in reference_orbits:
            r = orbit_km * scale
            canvas.create_oval(
                focus_x - r, focus_y - r,
                focus_x + r, focus_y + r,
                outline=color,
                dash=(4, 4)
            )

        # -----------------------------
        # Actual orbit
        # -----------------------------
        rx = a * scale
        ry = b * scale
        canvas.create_oval(
            cx - rx, cy - ry,
            cx + rx, cy + ry,
            outline="white",
            width=2
        )

        # -----------------------------
        # Output text
        # -----------------------------
        if system_mode.get() == "Solar System":
            a_str = f"{a / AU_KM:.3f} AU"
        else:
            a_str = f"{a:,.0f} km"

        info_label.config(
            text=f"System: {system_mode.get()}\n"
                 f"Eccentricity: {e:.4f}\n"
                 f"Semi-major axis: {a_str}"
        )

    # -----------------------------
    # Update input units on mode change
    # -----------------------------
    def update_units(*args):
        if system_mode.get() == "Solar System":
            apo_label.config(text="Apoapsis [AU]:")
            peri_label.config(text="Periapsis [AU]:")
        else:
            apo_label.config(text="Apoapsis [km]:")
            peri_label.config(text="Periapsis [km]:")

    system_mode.trace_add("write", update_units)

    # -----------------------------
    # UI layout
    # -----------------------------
    CANVAS_SIZE = 500

    frame = tk.Frame(root)
    frame.pack()

    mode_frame = tk.Frame(frame)
    mode_frame.pack(pady=5)

    tk.Label(mode_frame, text="System:").pack(side=tk.LEFT)

    tk.OptionMenu(
        mode_frame,
        system_mode,
        "Solar System",
        "Earth–Moon System"
    ).pack(side=tk.LEFT)

    input_frame = tk.Frame(frame)
    input_frame.pack(pady=10)

    peri_label = tk.Label(input_frame)
    peri_label.grid(row=0, column=0, sticky="e")

    peri_entry = tk.Entry(input_frame, width=15)
    peri_entry.grid(row=0, column=1, padx=5)

    apo_label = tk.Label(input_frame)
    apo_label.grid(row=1, column=0, sticky="e")

    apo_entry = tk.Entry(input_frame, width=15)
    apo_entry.grid(row=1, column=1, padx=5)

    tk.Button(
        input_frame,
        text="Draw Orbit",
        command=draw_orbit
    ).grid(row=0, column=2, rowspan=2, padx=10)

    canvas = tk.Canvas(frame, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="black")
    canvas.pack(pady=10)

    info_label = tk.Label(frame, justify=tk.LEFT)
    info_label.pack(pady=10)

    update_units()
    apo_entry.focus()


def parallaxe_distance_UI2(root):

    # Clear non-menu widgets
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu"]:
            widget.destroy()


    # Clear again except menus + buttons
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    def calculate(*args):
        try:
            ro = float(roi.get())
        except ValueError:
            result_label.config(text="Error: Invalid input, please enter a number.")
            return

        # parallax formula
        r = AU / ((pi / 180) * (ro / 3600))

        result_label.config(
            text=f"Estimated Distance\n"
                 f"----------------------\n"
                 f"[Ly]:   {r / ly:.3f}\n"
                 f"[Pc]:   {r / psc:.3f}\n"
                 f"[Mpc]:  {r / (psc * 1e6):.3f}\n"
        )

    frame = tk.Frame(root, width=1000, height=600)
    frame.pack()

    input_frame = tk.Frame(frame)
    input_frame.pack(pady=20)

    par_label = tk.Label(input_frame, text="Enter Parallax in [arc sec]")
    par_label.pack(side=tk.LEFT)

    roi = tk.Entry(input_frame)
    roi.pack(side=tk.LEFT)
    roi.bind("<Return>", calculate)

    calculate_button = tk.Button(input_frame, text="Calculate", command=calculate)
    calculate_button.pack(side=tk.LEFT, padx=10)

    result_label = tk.Label(frame, justify=tk.LEFT)
    result_label.pack(pady=50)





def photon_energy(wavelength):

    frequency = c / wavelength  # calculate frequency of photon
    energy_J = h * frequency  # calculate energy in Joules
    energy_eV = energy_J / eV  # convert to eV

    return energy_J, energy_eV


def spectrum_name(wavelength):
    if 10 ** -3 <= wavelength < 10 ** -1:
        return "Microwave"
    elif 10 ** -6 <= wavelength < 10 ** -3:
        return "Infrared"
    elif 10 ** -8 <= wavelength < 10 ** -6:
        return "Visible"
    elif 10 ** -11 <= wavelength < 10 ** -8:
        return "Ultraviolet"
    elif 10 ** -14 <= wavelength < 10 ** -11:
        return "X-ray"
    elif wavelength < 10 ** -14:
        return "Gamma-ray"
    else:
        return "Radio"




def photon_energy_spectrum_UI(root):
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    def calculate(*args):
        wavelengthi = wavelength_entry.get()
        try:
            wavelength = ast.literal_eval(wavelengthi)
        except (ValueError, SyntaxError):
            result_label.config(text="Invalid input. Please enter a valid number.")
            return

        energy_J, energy_eV = photon_energy(wavelength)
        spectrumname = spectrum_name(wavelength)

        result_label.config(text=f"{spectrumname}\n"
                                  f"------------------\n"
                                  f"{round(energy_J)} Joules\n"
                                  f"{round(energy_eV/1e-9, 9)} neV\n"
                                  f"{round(energy_eV, 9)} eV\n"
                                  f"{round(energy_eV/1e6, 5)} MeV\n"
                                  f"{round(energy_eV/1e9, 5)} GeV\n"
                                  f"{round(energy_eV/1e12, 5)} TeV")

    # Create the UI elements
    frame = tk.Frame(root, width=1000, height=600)
    frame.pack()

    input_frame = tk.Frame(frame)
    input_frame.pack(pady=20)

    wavelength_label = tk.Label(input_frame, text="Wavelength in [m]: ")
    wavelength_label.pack(side=tk.LEFT)

    wavelength_entry = tk.Entry(input_frame)
    wavelength_entry.pack(side=tk.LEFT)
    wavelength_entry.bind("<Return>", calculate)

    calculate_button = tk.Button(input_frame, text="Calculate", command=calculate)
    calculate_button.pack(side=tk.LEFT, padx=10)

    result_label = tk.Label(frame, justify=tk.LEFT)
    result_label.pack(pady=50)


MS_colors = ['blue', 'blue', 'cyan', 'green', 'yellow', 'orange', 'red']
MS_absmag = [5.5, 5.0, 4.0, 3.0, 2.0, 1.5, 0.0]
MS_sptype = ['O', 'B', 'A', 'F', 'G', 'K', 'M']





def spectral_class3_UI(root):
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()
    def calculate(*args):
        try:
            temp = float(temperature_entry.get())
        except ValueError:
            result_label.config(text="Error: Invalid input, please enter a number.")
            return

        if temp >= 30000:
            spectral_class = "O"
            color = "Blue"
        elif temp >= 10000:
            spectral_class = "B"
            color = "Blue-White"
        elif temp >= 7500:
            spectral_class = "A"
            color = "White"
        elif temp >= 6000:
            spectral_class = "F"
            color = "Yellow-White"
        elif temp >= 5200:
            spectral_class = "G"
            color = "Yellow"
        elif temp >= 3700:
            spectral_class = "K"
            color = "Orange"
        else:
            spectral_class = "M"
            color = "Red"

        # calculate peak wavelength and determine part of spectrum
        wavelength = (2.898 * 10 ** 6) / temp
        if wavelength < 0.01:
            spectrum_part = "Gamma rays"
        elif wavelength < 10:
            spectrum_part = "X-rays"
        elif wavelength < 400:
            spectrum_part = "Ultraviolet"
        elif wavelength < 700:
            spectrum_part = "Visible light"
        elif wavelength < 3000:
            spectrum_part = "Infrared"
        elif wavelength < 1000000:
            spectrum_part = "Microwaves"
        else:
            spectrum_part = "Radio waves"

        result_label.config(text=f"Spectral Class: {spectral_class} ({color})\n"
                                  f"Peak Wavelength: {wavelength:.3g} nm\n"
                                  f"Part of Spectrum: {spectrum_part}")

    # create the UI elements
    frame = tk.Frame(root, width=500, height=500)
    frame.pack()

    input_frame = tk.Frame(frame)
    input_frame.pack(pady=20)

    temperature_label = tk.Label(input_frame, text="Temperature in [K]: ",font=("Arial", 22))
    temperature_label.pack(side=tk.LEFT)

    temperature_entry = tk.Entry(input_frame)
    temperature_entry.pack(side=tk.LEFT)
    temperature_entry.bind("<Return>", calculate)
    calculate_button = tk.Button(input_frame, text="Calculate", command=calculate,font=("Arial", 22))
    calculate_button.pack(side=tk.LEFT, padx=10)

    result_label = tk.Label(frame, justify=tk.LEFT)
    result_label.pack(pady=50)





def schwarzschild_radius_UI2(root):
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    def calculate(*args):
        try:
            mass = float(mass_entry.get())
        except ValueError:
            result_label.config(text="Error: Invalid input, please enter a number.")
            return

        if mass < M_min:
            result_label.config(text="Error: Mass is less than minimum mass of 22 micrograms.")
        else:
            radius = 2 * G * mass / c ** 2
            result_label.config(text=
                f"Schwarzschild radius:\n"
                f"========================\n"
                f"[nm]: {radius * 10 ** 9:.3f} nm\n"
                f"------------------------\n"
                f"[m]: {radius:.3f} m\n"
                f"------------------------\n"
                f"[km]: {radius / 1000:.3f} km\n"
                f"------------------------\n"
                f"[R☉]: {radius / 6.957e8:.2f} R☉\n"
            )


    M_min = 2.2 * 10 ** -8  # Minimum mass in kg

    frame = tk.Frame(root, width=500, height=500)
    frame.pack()

    input_frame = tk.Frame(frame)
    input_frame.pack(pady=20)

    mass_label = tk.Label(input_frame, text="Mass in [kg]: ")
    mass_label.pack(side=tk.LEFT)

    mass_entry = tk.Entry(input_frame)
    mass_entry.pack(side=tk.LEFT)
    mass_entry.bind("<Return>", calculate)

    calculate_button = tk.Button(input_frame, text="Calculate", command=calculate)
    calculate_button.pack(side=tk.LEFT, padx=10)

    result_label = tk.Label(frame, justify=tk.LEFT)
    result_label.pack(pady=50)

    mass_entry.focus()


def hohmann_transfer_UI2(root):
    # clear existing widgets except menu and buttons
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    # central bodies (name: (mu [m^3/s^2], radius [m]))
    bodies = {
        "Earth": (3.986004418e14, 6.371e6),
        "Moon": (4.9048695e12, 1.7374e6),
        "Mars": (4.282837e13, 3.3895e6),
        "Venus": (3.24859e14, 6.0518e6),
        "Jupiter": (1.2668653e17, 6.9911e7),
        "Saturn": (3.7931187e16, 5.8232e7),
        "Sun": (1.32712440018e20, 6.9634e8),
    }

    selected_body = tk.StringVar(value="Earth")

    def calculate(*args):
        try:
            # user inputs are treated as altitudes above surface [m]
            a1 = float(start_apo_entry.get()) * 1000
            p1 = float(start_peri_entry.get()) * 1000
            a2 = float(final_apo_entry.get()) * 1000
            p2 = float(final_peri_entry.get()) * 1000
        except ValueError:
            result_label.config(text="Error: Invalid input, please enter numeric altitudes in meters.")
            return

        mu, Rbody = bodies[selected_body.get()]

        # validate altitudes
        if min(a1, p1, a2, p2) < 0:
            result_label.config(text="Error: Altitudes must be >= 0.")
            return

        # convert altitudes to radii (measured from body's center)
        r1a = a1 + Rbody
        r1p = p1 + Rbody
        r2a = a2 + Rbody
        r2p = p2 + Rbody

        # approximate circular orbit radii as average of apo and peri
        r1 = (r1a + r1p) / 2.0
        r2 = (r2a + r2p) / 2.0

        if r1 <= 0 or r2 <= 0:
            result_label.config(text="Error: Computed radius <= 0 (check inputs).")
            return

        # circular velocities
        v1 = math.sqrt(mu / r1)
        v2 = math.sqrt(mu / r2)

        # transfer orbit semi-major axis
        a_transfer = (r1 + r2) / 2.0

        # vis-viva for transfer velocities at r1 (peri) and r2 (apo)
        v_transfer_peri = math.sqrt(mu * (2.0 / r1 - 1.0 / a_transfer))
        v_transfer_apo  = math.sqrt(mu * (2.0 / r2 - 1.0 / a_transfer))

        # burns
        delta_v1 = abs(v_transfer_peri - v1)
        delta_v2 = abs(v2 - v_transfer_apo)
        total_delta_v = delta_v1 + delta_v2

        result_label.config(text=(
            f"Hohmann Transfer (central body: {selected_body.get()}):\n"
            f"================================================\n"
            f"Burns:\n"
            f"  ΔV₁ (departure) = {delta_v1/1000:.6f} km/s\n"
            f"  ΔV₂ (arrival)   = {delta_v2/1000:.6f} km/s\n"
            f"--------------------------------\n"
            f"Total ΔV = {total_delta_v/1000:.6f} km/s\n"
        ))

    # main frame: larger to fit fields
    frame = tk.Frame(root, width=700, height=600)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

    # body selector
    body_frame = tk.Frame(frame)
    body_frame.pack(anchor="w", pady=(6, 2))
    tk.Label(body_frame, text="Central body: ").pack(side=tk.LEFT)
    body_menu = tk.OptionMenu(body_frame, selected_body, *bodies.keys())
    body_menu.pack(side=tk.LEFT)

    input_frame = tk.Frame(frame)
    input_frame.pack(pady=10, anchor="w")

    labels = [
        "Start Apoapsis [altitude km]: ",
        "Start Periapsis [altitude km]: ",
        "Final Apoapsis [altitude km]: ",
        "Final Periapsis [altitude km]: "
    ]
    entries = []
    for text in labels:
        sub = tk.Frame(input_frame)
        sub.pack(anchor="w", pady=6)
        tk.Label(sub, text=text).pack(side=tk.LEFT)
        e = tk.Entry(sub, width=20)
        e.pack(side=tk.LEFT)
        e.bind("<Return>", calculate)
        entries.append(e)

    start_apo_entry, start_peri_entry, final_apo_entry, final_peri_entry = entries

    calculate_button = tk.Button(frame, text="Calculate ΔV", command=calculate)
    calculate_button.pack(pady=12)

    result_label = tk.Label(frame, justify=tk.LEFT, anchor="w")
    result_label.pack(fill=tk.X, padx=6, pady=6)

    start_apo_entry.focus()



def rocket_deltaV_UI5(root):
    # Clear old widgets except menus/buttons
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    g0 = 9.80665  # m/s²

    # --- Engine Isp presets ---
    isp_presets = {
        "Custom": "",
        "F-1 (263 s)": 263,
        "RS-25 (452 s)": 452,
        "J-2 (421 s)": 421,
        "RL10 (465 s)": 465,
        "Merlin 1D (311 s)": 311,
        "Raptor (350 s)": 350,
        "Hypergolic (320 s)": 320,
        "Vacuum Isp (380 s)": 380,
    }

    def calculate(*args):
        total_delta_v = 0.0
        total_burn_time = 0.0
        results = []

        try:
            stages = []
            for i in range(num_stages):
                wet_s = wet_entries[i].get().strip()
                dry_s = dry_entries[i].get().strip()
                isp_s = isp_entries[i].get().strip()
                thrust_s = thrust_entries[i].get().strip()

                # Skip blank rows
                if wet_s == dry_s == isp_s == thrust_s == "":
                    continue

                # Must fill all fields if one is filled
                if "" in (wet_s, dry_s, isp_s, thrust_s):
                    raise ValueError(f"Stage {i+1}: fill all fields or leave blank")

                wet_t = float(wet_s)
                dry_t = float(dry_s)
                isp = float(isp_s)
                thrust_kn = float(thrust_s)

                if wet_t <= 0 or dry_t <= 0 or isp <= 0 or thrust_kn <= 0:
                    raise ValueError(f"Stage {i+1}: all values must be > 0")
                if dry_t >= wet_t:
                    raise ValueError(f"Stage {i+1}: dry mass must be < wet mass")

                stages.append({
                    "index": i + 1,
                    "wet_kg": wet_t * 1000,
                    "dry_kg": dry_t * 1000,
                    "isp": isp,
                    "thrust_n": thrust_kn * 1000,
                })

            if not stages:
                result_label.config(text="No stages entered.")
                return

            # ---- Stage 1 = bottommost ----
            n = len(stages)
            mass_above_list = []
            for i in range(n):
                mass_above = sum(stages[j]["wet_kg"] for j in range(i + 1, n))
                mass_above_list.append(mass_above)

            total_launch_mass = sum(st["wet_kg"] for st in stages)
            total_launch_thrust = stages[0]["thrust_n"]
            total_launch_twr = total_launch_thrust / (total_launch_mass * g0)

            for i, st in enumerate(stages):
                wet = st["wet_kg"]
                dry = st["dry_kg"]
                isp = st["isp"]
                thrust = st["thrust_n"]

                mass_above = mass_above_list[i]
                m0 = wet + mass_above
                mf = dry + mass_above

                delta_v = isp * g0 * math.log(m0 / mf)

                mdot = thrust / (isp * g0)
                propellant_mass = wet - dry
                burn_time = propellant_mass / mdot

                twr = thrust / (m0 * g0)

                results.append((st["index"], delta_v, burn_time, twr))
                total_delta_v += delta_v
                total_burn_time += burn_time

        except ValueError as e:
            result_label.config(text=f"Error: {e}")
            return
        except Exception as e:
            result_label.config(text=f"Unexpected error: {e}")
            return

        # ---- Output ----
        out = "Multi-Stage Rocket ΔV Calculator\n"
        out += "====================================\n"
        out += "(Stage 1 = bottommost, burns first)\n\n"

        for idx, dv, bt, twr in results:
            warn = " ⚠️" if twr < 1.1 else ""
            out += (
                f"Stage {idx}: ΔV = {dv:7.1f} m/s ({dv/1000:.3f} km/s),  "
                f"Burn = {bt:7.1f} s,  "
                f"TWR = {twr:.2f}{warn}\n"
            )

        out += "------------------------------------\n"
        out += f"Total ΔV = {total_delta_v:7.1f} m/s ({total_delta_v/1000:.3f} km/s)\n"
        out += f"Total Burn Time = {total_burn_time:7.1f} s\n"
        out += f"Total Launch TWR = {total_launch_twr:.2f}\n"

        result_label.config(text=out)

    # ---- UI layout ----
    frame = tk.Frame(root, width=800, height=700)
    frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    title = tk.Label(frame, text="Multi-Stage Rocket ΔV Calculator", font=("Arial", 12, "bold"))
    title.pack(pady=8)

    note = tk.Label(frame, text="Enter stages bottom → top (Stage 1 = bottommost). Leave unused rows blank.")
    note.pack()

    num_stages = 5

    input_frame = tk.Frame(frame)
    input_frame.pack(pady=8, anchor="w")

    header = tk.Frame(input_frame)
    header.pack(fill=tk.X)
    tk.Label(header, text="Stage", width=8).grid(row=0, column=0)
    tk.Label(header, text="Wet [t]", width=12).grid(row=0, column=1)
    tk.Label(header, text="Dry [t]", width=12).grid(row=0, column=2)
    tk.Label(header, text="Isp [s]", width=16).grid(row=0, column=3)
    tk.Label(header, text="Thrust [kN]", width=14).grid(row=0, column=4)

    wet_entries, dry_entries, isp_entries, thrust_entries = [], [], [], []

    for i in range(num_stages):
        row = tk.Frame(input_frame)
        row.pack(anchor="w", pady=2)

        tk.Label(row, text=f"{i+1}", width=8).grid(row=0, column=0)
        wet = tk.Entry(row, width=12); wet.grid(row=0, column=1, padx=2)
        dry = tk.Entry(row, width=12); dry.grid(row=0, column=2, padx=2)

        isp_var = tk.StringVar()
        isp_dropdown = tk.OptionMenu(row, isp_var, *isp_presets.keys())
        isp_dropdown.config(width=14)
        isp_dropdown.grid(row=0, column=3, padx=2)

        isp_entry = tk.Entry(row, width=8)
        isp_entry.grid(row=0, column=3, padx=80)  # overlay entry
        isp_entries.append(isp_entry)

        def update_isp_entry(var=isp_var, entry=isp_entry):
            val = isp_presets[var.get()]
            entry.delete(0, tk.END)
            if val != "":
                entry.insert(0, str(val))

        isp_var.trace_add("write", lambda *_, var=isp_var, entry=isp_entry: update_isp_entry(var, entry))

        thr = tk.Entry(row, width=14); thr.grid(row=0, column=4, padx=2)
        wet.bind("<Return>", calculate)
        dry.bind("<Return>", calculate)
        isp_entry.bind("<Return>", calculate)
        thr.bind("<Return>", calculate)
        wet_entries.append(wet)
        dry_entries.append(dry)
        thrust_entries.append(thr)

    calc_btn = tk.Button(frame, text="Calculate ΔV and Burn Time", command=calculate)
    calc_btn.pack(pady=10)

    result_label = tk.Label(frame, justify=tk.LEFT, anchor="w")
    result_label.pack(fill=tk.X, padx=6, pady=6)

    wet_entries[0].focus()

    def stellar_magnitude_UI(root):
        # Clear window except menu/buttons
        for widget in root.winfo_children():
            if widget.winfo_class() not in ["Menu", "Button"]:
                widget.destroy()

        def calculate(*args):
            try:
                m = float(apparent_entry.get())
                d = float(distance_entry.get())

                if d <= 0:
                    result_label.config(text="Error: Distance must be greater than 0.")
                    return

                # Absolute magnitude formula
                M = m - 5 * (math.log10(d) - 1)

                result_label.config(text=
                                    f"Stellar Magnitude Calculator\n"
                                    f"=============================\n"
                                    f"Apparent magnitude (m): {m}\n"
                                    f"Distance: {d} parsecs\n"
                                    f"-----------------------------\n"
                                    f"Absolute magnitude (M): {M:.3f}\n"
                                    )

            except ValueError:
                result_label.config(text="Error: Invalid input. Please enter numbers.")

        # --- UI layout ---
        frame = tk.Frame(root, width=500, height=400)
        frame.pack()

        title = tk.Label(frame, text="Stellar Magnitude Calculator", font=("Arial", 12, "bold"))
        title.pack(pady=10)

        input_frame = tk.Frame(frame)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Apparent Magnitude (m): ").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        apparent_entry = tk.Entry(input_frame, width=15)
        apparent_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Distance [parsecs]: ").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        distance_entry = tk.Entry(input_frame, width=15)
        distance_entry.grid(row=1, column=1, padx=5, pady=5)

        calculate_button = tk.Button(frame, text="Calculate", command=calculate)
        calculate_button.pack(pady=10)

        result_label = tk.Label(frame, justify="left")
        result_label.pack(pady=20)

        apparent_entry.bind("<Return>", calculate)
        distance_entry.bind("<Return>", calculate)
        apparent_entry.focus()


def stellar_magnitude_UI2(root):
    # Clear old widgets except menu/buttons
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    def calculate(*args):
        try:
            m = float(apparent_entry.get())
            d = float(distance_entry.get())

            if d <= 0:
                result_label.config(text="Error: Distance must be greater than 0.")
                return

            # Convert to parsecs if user selected light-years
            unit = unit_var.get()
            if unit == "Light-years":
                d /= 3.26156  # 1 pc = 3.26156 ly

            # Calculate absolute magnitude
            M = m - 5 * (math.log10(d) - 1)

            result_label.config(text=
                f"Stellar Magnitude Calculator\n"
                f"=============================\n"
                f"Apparent magnitude (m): {m}\n"
                f"Distance: {d:.3f} parsecs ({d*3.26156:.3f} ly)\n"
                f"-----------------------------\n"
                f"Absolute magnitude (M): {M:.3f}\n"
            )

        except ValueError:
            result_label.config(text="Error: Invalid input. Please enter numbers.")

    # --- UI layout ---
    frame = tk.Frame(root, width=520, height=420)
    frame.pack()

    title = tk.Label(frame, text="Stellar Magnitude Calculator", font=("Arial", 12, "bold"))
    title.pack(pady=10)

    input_frame = tk.Frame(frame)
    input_frame.pack(pady=20)

    tk.Label(input_frame, text="Apparent Magnitude (m): ").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    apparent_entry = tk.Entry(input_frame, width=15)
    apparent_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="Distance: ").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    distance_entry = tk.Entry(input_frame, width=15)
    distance_entry.grid(row=1, column=1, padx=5, pady=5)

    unit_var = tk.StringVar(value="Parsecs")
    unit_menu = tk.OptionMenu(input_frame, unit_var, "Parsecs", "Light-years")
    unit_menu.grid(row=1, column=2, padx=5, pady=5)

    calculate_button = tk.Button(frame, text="Calculate", command=calculate)
    calculate_button.pack(pady=10)

    result_label = tk.Label(frame, justify="left")
    result_label.pack(pady=20)

    apparent_entry.bind("<Return>", calculate)
    distance_entry.bind("<Return>", calculate)
    apparent_entry.focus()


def roche_limit_UI(root):
    # Clear existing widgets except menu/buttons
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    def calculate(*args):
        try:
            R_primary = float(radius_entry.get()) * 1000   # km → m
            density_primary = float(rho_primary_entry.get())  # kg/m^3
            density_secondary = float(rho_secondary_entry.get())

            if density_primary <= 0 or density_secondary <= 0 or R_primary <= 0:
                result_label.config(text="Error: All values must be positive.")
                return

            ratio = (density_primary / density_secondary) ** (1/3)

            roche_fluid = 2.44 * R_primary * ratio
            roche_rigid = 1.26 * R_primary * ratio

            result_label.config(text=
                f"Roche Limit Calculator\n"
                f"==============================\n"
                f"Primary Radius: {R_primary/1000:.3f} km\n"
                f"Density Primary: {density_primary} kg/m³\n"
                f"Density Secondary: {density_secondary} kg/m³\n"
                f"------------------------------\n"
                f"Fluid Roche Limit: {roche_fluid/1000:.3f} km\n"
                f"                             {roche_fluid/radiusearth:.3f} rE\n"
                f"Rigid Roche Limit: {roche_rigid/1000:.3f} km\n"
                f"                             {roche_rigid/radiusearth:.3f} rE\n"
            )
        except ValueError:
            result_label.config(text="Error: Please enter valid numbers.")

    # UI layout
    frame = tk.Frame(root, width=520, height=420)
    frame.pack()

    title = tk.Label(frame, text="Roche Limit Calculator", font=("Arial", 12, "bold"))
    title.pack(pady=10)

    input_frame = tk.Frame(frame)
    input_frame.pack(pady=20)

    tk.Label(input_frame, text="Primary Radius [km]: ").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    radius_entry = tk.Entry(input_frame, width=15)
    radius_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="Primary Density [kg/m³]: ").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    rho_primary_entry = tk.Entry(input_frame, width=15)
    rho_primary_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="Secondary Density [kg/m³]: ").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    rho_secondary_entry = tk.Entry(input_frame, width=15)
    rho_secondary_entry.grid(row=2, column=1, padx=5, pady=5)

    calculate_button = tk.Button(frame, text="Calculate", command=calculate)
    calculate_button.pack(pady=10)

    result_label = tk.Label(frame, justify="left")
    result_label.pack(pady=20)

    radius_entry.bind("<Return>", calculate)
    rho_primary_entry.bind("<Return>", calculate)
    rho_secondary_entry.bind("<Return>", calculate)

    radius_entry.focus()
