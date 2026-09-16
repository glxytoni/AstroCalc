import math
import ast
import tkinter as tk
from scipy.integrate import quad
from astropy.cosmology import Planck15
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

CANVAS_SIZE = 420

SOLAR_SYSTEM = {

    "sun": {
        "radius": 6.9634e8,
        "mass": 1.98847e30,
        "gravity": 274,
        "color": "#FFD54A",
        "type": "star"
    },

    "mercury": {
        "radius": 2.4397e6,
        "mass": 3.3011e23,
        "gravity": 3.7,
        "color": "#8C8C8C",
        "type": "planet"
    },

    "venus": {
        "radius": 6.0518e6,
        "mass": 4.8675e24,
        "gravity": 8.87,
        "color": "#E6C87A",
        "type": "planet"
    },

    "earth": {
        "radius": 6.371e6,
        "mass": 5.9722e24,
        "gravity": 9.80665,
        "color": "#2B6FFF",
        "type": "planet"
    },

    "mars": {
        "radius": 3.3895e6,
        "mass": 6.4171e23,
        "gravity": 3.72076,
        "color": "#C1440E",
        "type": "planet"
    },

    "jupiter": {
        "radius": 6.9911e7,
        "mass": 1.8982e27,
        "gravity": 24.79,
        "color": "#D9B38C",
        "type": "planet"
    },

    "saturn": {
        "radius": 5.8232e7,
        "mass": 5.6834e26,
        "gravity": 10.44,
        "color": "#E8D8A8",
        "type": "planet"
    },

    "uranus": {
        "radius": 2.5362e7,
        "mass": 8.6810e25,
        "gravity": 8.69,
        "color": "#8DE0E8",
        "type": "planet"
    },

    "neptune": {
        "radius": 2.4622e7,
        "mass": 1.02413e26,
        "gravity": 11.15,
        "color": "#4169E1",
        "type": "planet"
    }
}

#=====  Backend shi ===========================================

def redshift_to_proper_distance(z):
    """
    Calculate the present-day proper (comoving) distance
    from cosmological redshift using Planck15 cosmology.

    Returns distance in meters.
    """

    if z < 0:
        raise ValueError("Redshift cannot be negative.")

    c = 299792458.0  # m/s

    H0 = Planck15.H0.to_value("1/s")
    omega_m = Planck15.Om0
    omega_lambda = Planck15.Ode0
    omega_r = Planck15.Ogamma0 + Planck15.Onu0

    def integrand(z_prime):
        E = (
            omega_m * (1.0 + z_prime) ** 3
            + omega_r * (1.0 + z_prime) ** 4
            + omega_lambda
        ) ** 0.5

        return 1.0 / E

    integral = quad(
        integrand,
        0.0,
        z,
        epsabs=1e-10,
        epsrel=1e-10
    )[0]

    distance_m = (c / H0) * integral

    return distance_m


def redshift_distance_UI(root):

    window = root

    input_frame = tk.Frame(window)
    input_frame.pack(pady=20)

    tk.Label(
        input_frame,
        text="Redshift (z):",
        font=("Arial", 16)
    ).grid(row=0, column=0, padx=10, pady=10)

    z_entry = tk.Entry(
        input_frame,
        font=("Arial", 16),
        width=15
    )
    z_entry.grid(row=0, column=1, padx=10, pady=10)

    result_label = tk.Label(
        window,
        text="",
        font=("Arial", 15),
        justify="left"
    )
    result_label.pack(pady=20)

    def calculate(*args):

        try:
            z = float(z_entry.get())

            if z < 0:
                raise ValueError

            distance_m = redshift_to_proper_distance(z)

            distance_pc = distance_m / psc
            distance_kpc = distance_pc / 1e3
            distance_mpc = distance_pc / 1e6
            distance_ly = distance_m / ly

            result_label.config(
                text=(
                    f"Redshift: z = {z:g}\n\n"
                    f"Proper distance today:\n"
                    f"{distance_mpc:,.3f} Mpc\n"
                    f"{distance_ly / 1e9:,.3f} billion ly\n\n"
                    f"Distance in parsecs:\n"
                    f"{distance_pc:,.3e} pc\n\n"
                    f"Distance in meters:\n"
                    f"{distance_m:,.3e} m"
                )
            )

        except ValueError:
            result_label.config(
                text="Please enter a valid non-negative redshift."
            )

    ttk.Button(
        window,
        text="Calculate",
        command=calculate
    ).pack(pady=10)

    z_entry.bind("<Return>", calculate)
    z_entry.focus()





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


def relativistic_kinetic_energy_UI(root):

    import tkinter as tk
    import math

    c = 299792458

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    tk.Label(frame,text="Mass [kg]").grid(row=0,column=0)
    mass_entry = tk.Entry(frame)
    mass_entry.grid(row=0,column=1)

    tk.Label(frame,text="Velocity [m/s]").grid(row=1,column=0)
    vel_entry = tk.Entry(frame)
    vel_entry.grid(row=1,column=1)

    result = tk.Label(frame,justify=tk.LEFT)
    result.grid(row=3,column=0,columnspan=2)


    def calculate():

        try:
            m = float(mass_entry.get())
            v = float(vel_entry.get())

            if v >= c:
                result.config(text="Velocity must be below c")
                return

            gamma = 1 / math.sqrt(1-(v*v)/(c*c))

            KE = (gamma-1)*m*c*c


            result.config(
                text=
                f"Lorentz factor γ = {gamma:.6g}\n"
                f"Kinetic Energy = {KE:.6e} J\n"
                f"Kg of TNT      = {KE/4.2e6:.2f} Kg\n"
                f"t of TNT      = {KE/4.184e9:.3f} t\n"
                f"Kt of TNT      = {KE/4.184e12:.2f} kt\n"
                f"Mt of TNT      = {KE/4.184e15:.2} Mt"

            )

        except:
            result.config(text="Invalid input")


    tk.Button(
        frame,
        text="Calculate",
        command=calculate
    ).grid(row=2,column=0,columnspan=2)






def relativistic_kinetic_energy_UI2(root):

    import tkinter as tk
    import math

    c = 299792458

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    # False = m/s
    # True = fraction of c
    velocity_mode = tk.BooleanVar(value=False)

    tk.Label(frame, text="Mass [kg]").grid(row=0, column=0)

    mass_entry = tk.Entry(frame)
    mass_entry.grid(row=0, column=1)

    velocity_label = tk.Label(frame, text="Velocity [m/s]")
    velocity_label.grid(row=1, column=0)

    vel_entry = tk.Entry(frame)
    vel_entry.grid(row=1, column=1)

    result = tk.Label(frame, justify=tk.LEFT)
    result.grid(row=4, column=0, columnspan=2, pady=10)

    def toggle_velocity_mode():

        velocity_mode.set(not velocity_mode.get())

        if velocity_mode.get():
            velocity_label.config(
                text="Velocity [fraction of c]"
            )
            mode_button.config(
                text="Input Mode: Fraction of c"
            )
        else:
            velocity_label.config(
                text="Velocity [m/s]"
            )
            mode_button.config(
                text="Input Mode: m/s"
            )

    def smart_format(value):

        if value == 0:
            return "0"

        if 0.001 <= abs(value) < 100000:
            return f"{value:.3f}"

        return f"{value:.3e}"


    def calculate(*args):

        try:
            m = float(mass_entry.get())
            v_input = float(vel_entry.get())

            if velocity_mode.get():
                v = v_input * c
            else:
                v = v_input

            if v >= c:
                result.config(
                    text="Velocity must be below c"
                )
                return

            if v < 0:
                result.config(
                    text="Velocity cannot be negative"
                )
                return

            if m <= 0:
                result.config(
                    text="Mass must be positive"
                )
                return

            gamma = 1 / math.sqrt(
                1 - (v * v) / (c * c)
            )

            KE = (gamma - 1) * m * c * c

            if KE < 4.184e18:
                result.config(

                text=
                f"Lorentz factor γ = {gamma:.8g}\n"
                f"--------------------------------\n"
                f"Kinetic Energy = {smart_format(KE)} J\n"
                f"--------------------------------\n"
                f"Kg TNT = {smart_format(KE / 4.184e6)} kg\n"
                f"t  TNT = {smart_format(KE / 4.184e9)} t\n"
                f"Kt TNT = {smart_format(KE / 4.184e12)} kt\n"
                f"Mt TNT = {smart_format(KE / 4.184e15)} Mt\n"
                f"Gt TNT = {smart_format(KE / 4.184e18)} Gt"


                )
                return

            if KE > 4.184e18:
                result.config(

                text=
                f"Lorentz factor γ = {gamma:.8g}\n"
                f"--------------------------------\n"
                f"Kinetic Energy = {smart_format(KE)} J\n"
                f"--------------------------------\n"
                f"Mt TNT = {smart_format(KE / 4.184e15)} Mt\n"
                f"Gt TNT = {smart_format(KE / 4.184e18)} Gt\n"       
                f"Hiroshimas = {smart_format(KE / (4.184e12 * 15))} Little Boys\n"
                f"Tsar Bombs = {smart_format(KE / (4.184e18 * 50))} Tsars\n"
                f"dino killers = {smart_format(KE / 1e26)} Meteors\n"
                f"Type 1a = {smart_format(KE / 1.5e44)} Supernovae"
                )
                return



        except ValueError:
            result.config(
                text="Invalid input"
            )

    mode_button = tk.Button(
        frame,
        text="Input Mode: m/s",
        command=toggle_velocity_mode
    )
    mode_button.grid(
        row=2,
        column=0,
        columnspan=2,
        pady=5
    )

    calculate_button = tk.Button(
        frame,
        text="Calculate",
        command=calculate
    )
    calculate_button.grid(
        row=3,
        column=0,
        columnspan=2
    )

    mass_entry.bind("<Return>", calculate)
    vel_entry.bind("<Return>", calculate)

    mass_entry.focus()




def relativistic_kinetic_energy_UI3(root):
    import tkinter as tk
    import math

    # clear screen except menu/buttons
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()


    c = 299_792_458  # m/s


    # -------------------------
    # UNIT FORMATTERS
    # -------------------------

    def format_energy(joules):

        ev = joules / 1.602176634e-19

        units = [
            ("eV", 1),
            ("keV", 1e3),
            ("MeV", 1e6),
            ("GeV", 1e9),
            ("TeV", 1e12),
            ("PeV", 1e15),
            ("EeV", 1e18),
        ]

        if ev == 0:
            return "0 eV"

        for name, factor in reversed(units):
            if abs(ev) >= factor:
                return f"{ev/factor:.4g} {name}"

        return f"{ev:.4g} eV"


    def format_mass(kg):

        units = [
            ("kg", 1),
            ("t", 1e3),
            ("kt", 1e6),
            ("Mt", 1e9),
            ("Gt", 1e12),

        ]

        if kg == 0:
            return "0 kg"

        for name, factor in reversed(units):
            if abs(kg) >= factor:
                return f"{kg/factor:.4g} {name}"

        return f"{kg:.4g} kg"



    # -------------------------
    # CALCULATE
    # -------------------------

    def calculate(*args):

        try:
            mass = float(mass_entry.get())
            velocity = float(velocity_entry.get())

        except ValueError:
            result_label.config(
                text="Error: Invalid input"
            )
            return


        if mass <= 0:
            result_label.config(
                text="Mass must be positive"
            )
            return


        if velocity >= c:
            result_label.config(
                text="Velocity must be below c"
            )
            return


        if velocity < 0:
            result_label.config(
                text="Velocity cannot be negative"
            )
            return


        gamma = 1 / math.sqrt(
            1 - (velocity**2 / c**2)
        )


        rest_energy = mass * c**2

        total_energy = gamma * rest_energy

        kinetic_energy = total_energy - rest_energy


        result_label.config(
            text=(
                f"Fraction of c:\n"
                f"{velocity/c:.8f}\n"
                f"------------------------\n"
                f"Lorentz factor γ:\n"
                f"{gamma:.8g}\n"
                f"------------------------\n"
                f"Rest Energy:\n"
                f"{format_energy(rest_energy)}\n"
                f"------------------------\n"
                f"Kinetic Energy:\n"
                f"{format_energy(kinetic_energy)}\n"
                f"------------------------\n"
                f"Total Relativistic Energy:\n"
                f"{format_energy(total_energy)}\n"
                f"------------------------\n"
                f"Equivalent kinetic mass:\n"
                f"{format_mass(kinetic_energy/c**2)}"
            )
        )


    # -------------------------
    # UI
    # -------------------------

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)


    input_frame = tk.Frame(frame)
    input_frame.pack(pady=10)


    tk.Label(
        input_frame,
        text="Mass [kg]: "
    ).grid(row=0, column=0, sticky="w")


    mass_entry = tk.Entry(input_frame)
    mass_entry.grid(row=0, column=1)


    tk.Label(
        input_frame,
        text="Velocity [m/s]: "
    ).grid(row=1, column=0, sticky="w")


    velocity_entry = tk.Entry(input_frame)
    velocity_entry.grid(row=1, column=1)


    mass_entry.bind("<Return>", calculate)
    velocity_entry.bind("<Return>", calculate)


    tk.Button(
        frame,
        text="Calculate",
        command=calculate
    ).pack(pady=10)


    result_label = tk.Label(
        frame,
        justify=tk.LEFT,
        anchor="w"
    )
    result_label.pack(pady=10)


    mass_entry.focus()



def relativistic_kinetic_energy_UI4(root):
    import tkinter as tk
    import math

    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    c = 299_792_458
    e_charge = 1.602176634e-19  # J per eV

    # -------------------------
    # PARTICLE MASS DATABASE (kg)
    # -------------------------
    particles = {
        "Electron": 9.1093837015e-31,
        "Muon": 1.883531627e-28,
        "Tau": 3.16754e-27,
        "Up quark (~constituent)": 3.0e-30,
        "Down quark (~constituent)": 5.0e-30,
        "Proton": 1.67262192369e-27,
        "Neutron": 1.67492749804e-27,
        "Higgs boson": 2.24e-25,
    }

    # -------------------------
    # FORMATTERS
    # -------------------------
    def format_energy(joules):
        ev = joules / e_charge
        units = [("eV", 1), ("keV", 1e3), ("MeV", 1e6), ("GeV", 1e9),
                  ("TeV", 1e12), ("PeV", 1e15), ("EeV", 1e18)]

        if ev == 0:
            return "0 eV"

        for name, factor in reversed(units):
            if abs(ev) >= factor:
                return f"{ev/factor:.4g} {name}"

        return f"{ev:.4g} eV"

    def format_mass(kg):
        units = [("kg", 1), ("t", 1e3), ("kt", 1e6), ("Mt", 1e9)]
        if kg == 0:
            return "0 kg"

        for name, factor in reversed(units):
            if abs(kg) >= factor:
                return f"{kg/factor:.4g} {name}"

        return f"{kg:.4g} kg"

    # -------------------------
    # CALCULATION
    # -------------------------
    def calculate(*args):
        try:
            mass = particles[particle_var.get()]
        except KeyError:
            result_label.config(text="Invalid particle selection")
            return

        mode = mode_var.get()

        try:
            if mode == "Velocity → Energy":
                velocity = float(entry1.get())

                if velocity < 0 or velocity >= c:
                    result_label.config(text="Velocity must be 0 ≤ v < c")
                    return

                beta = velocity / c
                gamma = 1 / math.sqrt(1 - beta**2)

            else:  # Energy → Velocity
                energy_ev = float(entry1.get())
                energy = energy_ev * e_charge

                rest_energy = mass * c**2
                gamma = energy / rest_energy

                if gamma < 1:
                    result_label.config(text="Energy must be ≥ rest energy")
                    return

                beta = math.sqrt(1 - 1 / gamma**2)
                velocity = beta * c

        except ValueError:
            result_label.config(text="Invalid numeric input")
            return

        rest_energy = mass * c**2
        total_energy = gamma * rest_energy
        kinetic_energy = total_energy - rest_energy

        result_label.config(text=
            f"Particle mass:\n{format_mass(mass)}\n"
            f"------------------------\n"
            f"β = v/c:\n{beta:.10f}\n"
            f"Velocity:\n{velocity:.6e} m/s\n"
            f"------------------------\n"
            f"Lorentz factor γ:\n{gamma:.8g}\n"
            f"------------------------\n"
            f"Rest Energy:\n{format_energy(rest_energy)}\n"
            f"Kinetic Energy:\n{format_energy(kinetic_energy)}\n"
            f"Total Energy:\n{format_energy(total_energy)}"
        )

    # -------------------------
    # UI
    # -------------------------
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    input_frame = tk.Frame(frame)
    input_frame.pack(pady=10)

    # particle dropdown
    tk.Label(input_frame, text="Particle:").grid(row=0, column=0, sticky="w")

    particle_var = tk.StringVar(value="Electron")
    tk.OptionMenu(input_frame, particle_var, *particles.keys()).grid(row=0, column=1)

    # mode selector
    mode_var = tk.StringVar(value="Velocity → Energy")

    tk.Label(input_frame, text="Mode:").grid(row=1, column=0, sticky="w")
    tk.OptionMenu(input_frame, mode_var,
                  "Velocity → Energy",
                  "Energy → Velocity").grid(row=1, column=1)

    # input field
    tk.Label(input_frame, text="Input:").grid(row=2, column=0, sticky="w")
    entry1 = tk.Entry(input_frame)
    entry1.grid(row=2, column=1)

    def update_label(*args):
        if mode_var.get() == "Velocity → Energy":
            entry1_label.config(text="Velocity [m/s]")
        else:
            entry1_label.config(text="Energy [eV]")

    entry1_label = tk.Label(input_frame, text="Velocity [m/s]")
    entry1_label.grid(row=2, column=2, padx=10)

    mode_var.trace_add("write", update_label)

    # buttons
    tk.Button(frame, text="Calculate", command=calculate).pack(pady=10)

    result_label = tk.Label(frame, justify=tk.LEFT, anchor="w")
    result_label.pack(pady=10)

    entry1.bind("<Return>", calculate)

#====================================================================================
def hohmann_transfer_UI4(root):
    import tkinter as tk
    import math

    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    selected_body = tk.StringVar(value="Earth")

    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    body_frame = tk.Frame(frame)
    body_frame.pack(anchor="w")

    tk.Label(
        body_frame,
        text="Central body: "
    ).pack(side=tk.LEFT)

    tk.OptionMenu(
        body_frame,
        selected_body,
        *[b.title() for b in SOLAR_SYSTEM.keys()]
    ).pack(side=tk.LEFT)


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

        tk.Label(
            row,
            text=text
        ).pack(side=tk.LEFT)

        e = tk.Entry(row, width=16)
        e.pack(side=tk.LEFT)

        entries.append(e)

    start_alt_entry, final_alt_entry = entries


    CANVAS_SIZE = 420

    canvas = tk.Canvas(
        frame,
        width=CANVAS_SIZE,
        height=CANVAS_SIZE,
        bg="black"
    )
    canvas.pack(pady=10)


    result_label = tk.Label(
        frame,
        justify=tk.LEFT,
        anchor="w"
    )
    result_label.pack(fill=tk.X, pady=6)


    def calculate():

        try:
            h1 = float(start_alt_entry.get()) * 1000
            h2 = float(final_alt_entry.get()) * 1000

        except ValueError:
            result_label.config(
                text="Error: Invalid altitude input."
            )
            return


        if h1 < 0 or h2 < 0:
            result_label.config(
                text="Error: Altitudes must be >= 0"
            )
            return


        # -----------------------
        # BODY LOOKUP
        # -----------------------

        body_key = selected_body.get().lower()

        body = SOLAR_SYSTEM[body_key]

        R = body["radius"]

        mu = G * body["mass"]


        # -----------------------
        # ORBIT CALCULATIONS
        # -----------------------

        r1 = R + h1
        r2 = R + h2


        v1 = math.sqrt(mu / r1)
        v2 = math.sqrt(mu / r2)


        a_t = (r1 + r2) / 2

        vtp = math.sqrt(
            mu * (2/r1 - 1/a_t)
        )

        vta = math.sqrt(
            mu * (2/r2 - 1/a_t)
        )


        dv1 = abs(vtp - v1)
        dv2 = abs(v2 - vta)


        result_label.config(
            text=(
                f"Hohmann Transfer ({body_key.title()}):\n"
                f"ΔV₁ = {dv1/1000:.6f} km/s\n"
                f"ΔV₂ = {dv2/1000:.6f} km/s\n"
                f"Total ΔV = {(dv1+dv2)/1000:.6f} km/s"
            )
        )


        # -----------------------
        # DRAWING
        # -----------------------

        canvas.delete("all")

        cx = cy = CANVAS_SIZE / 2


        scale = compute_orbit_scale(
            CANVAS_SIZE,
            [
                r1,
                r2,
                a_t * (1 + abs(r2-r1)/(r2+r1))
            ]
        )


        # Sun = solar mode
        # Earth = earth/moon mode
        if body_key == "earth":
            mode = "earth_moon"
        else:
            mode = "solar"

        body_color = SOLAR_SYSTEM[body_key].get(
            "color",
            "#FFFFFF"
        )


        draw_central_body(
            canvas,
            cx,
            cy,
            R,
            scale,
            body_color
        )


        draw_reference_orbits(
            canvas,
            mode,
            scale,
            cx,
            cy
        )


        # starting circular orbit
        draw_kepler_orbit(
            canvas,
            r1,
            0,
            scale,
            cx,
            cy
        )


        # transfer ellipse
        e_t = abs(r2-r1)/(r2+r1)

        draw_kepler_orbit(
            canvas,
            a_t,
            e_t,
            scale,
            cx,
            cy
        )


        # final circular orbit
        draw_kepler_orbit(
            canvas,
            r2,
            0,
            scale,
            cx,
            cy
        )


    tk.Button(
        frame,
        text="Calculate ΔV",
        command=calculate
    ).pack(pady=8)


    start_alt_entry.focus()


# OV_UI2 breaks if orbit is hyperbolic (numbers are correct the orbit drawing tool doenst work

def orbit_visualizer_UI2(root):
    import math
    import tkinter as tk

    # ---- Clear UI ----
    for widget in root.winfo_children():
        if widget.winfo_class() not in ["Menu", "Button"]:
            widget.destroy()

    # ---- Central bodies ----
    bodies = {
        "Sun":   (1.32712440018e20, 6.9634e8, "solar"),
        "Earth": (3.986004418e14,   6.371e6,  "earth_moon"),
    }

    selected_body = tk.StringVar(value="Earth")
    input_mode = tk.StringVar(value="Apo/Peri")

    # ---- Main frame ----
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

    # ---- Controls ----
    top = tk.Frame(frame)
    top.pack(anchor="w")

    tk.Label(top, text="Central body: ").pack(side=tk.LEFT)
    tk.OptionMenu(top, selected_body, *bodies.keys()).pack(side=tk.LEFT, padx=5)

    tk.Label(top, text="Input mode: ").pack(side=tk.LEFT, padx=(20, 0))
    tk.OptionMenu(top, input_mode, "Apo/Peri", "Velocity @ Periapsis").pack(side=tk.LEFT)

    # ---- Inputs ----
    input_frame = tk.Frame(frame)
    input_frame.pack(anchor="w", pady=10)

    entries = {}

    def make_entry(label):
        row = tk.Frame(input_frame)
        row.pack(anchor="w", pady=4)
        tk.Label(row, text=label, width=28, anchor="w").pack(side=tk.LEFT)
        e = tk.Entry(row, width=18)
        e.pack(side=tk.LEFT)
        return e

    peri_entry = make_entry("Periapsis altitude [km]:")
    apo_entry  = make_entry("Apoapsis altitude [km]:")

    vel_entry  = make_entry("Velocity at periapsis [km/s]:")

    # ---- Canvas ----
    canvas = tk.Canvas(frame, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="black")
    canvas.pack(pady=10)

    result_label = tk.Label(frame, justify=tk.LEFT)
    result_label.pack(anchor="w")

    # ---- Mode switching ----
    def update_mode(*args):
        if input_mode.get() == "Apo/Peri":
            apo_entry.config(state="normal")
            vel_entry.config(state="disabled")
        else:
            apo_entry.config(state="disabled")
            vel_entry.config(state="normal")

    input_mode.trace_add("write", update_mode)
    update_mode()

    # ---- Calculate + draw ----
    def calculate():
        try:
            peri_km = float(peri_entry.get())
        except ValueError:
            result_label.config(text="Invalid periapsis input.")
            return

        body_mu, body_radius, mode = bodies[selected_body.get()]

        r_p = body_radius + peri_km * 1000

        # ---- Determine orbit from mode ----
        if input_mode.get() == "Apo/Peri":
            try:
                apo_km = float(apo_entry.get())
            except ValueError:
                result_label.config(text="Invalid apoapsis input.")
                return

            r_a = body_radius + apo_km * 1000

            a = (r_p + r_a) / 2
            e = abs(r_a - r_p) / (r_a + r_p)

        else:
            try:
                v_p = float(vel_entry.get()) * 1000
            except ValueError:
                result_label.config(text="Invalid velocity input.")
                return

            inv_a = 2 / r_p - v_p ** 2 / body_mu

            if abs(inv_a) < 1e-12:
                a = float("inf")
                e = 1.0
            else:
                a = 1 / inv_a
                e = abs(1 - r_p / a)

        # ---- Drawing ----
        canvas.delete("all")
        cx = cy = CANVAS_SIZE / 2

        max_r = max(r_p * 2, abs(a) * (1 + e))
        scale = compute_orbit_scale(CANVAS_SIZE, [max_r])

        body_color = "yellow" if selected_body.get() == "Sun" else "blue"

        draw_central_body(
            canvas,
            cx,
            cy,
            body_radius,
            scale,
            color=body_color
        )

        draw_reference_orbits(canvas, mode, scale, cx, cy)

        draw_kepler_orbit(
            canvas,
            a,
            e,
            scale,
            cx,
            cy,
            color="white"
        )

        orbit_type = (
            "Elliptic" if e < 1 else
            "Parabolic" if abs(e - 1) < 1e-3 else
            "Hyperbolic"
        )

        result_label.config(text=(
            f"Orbit type: {orbit_type}\n"
            f"Semi-major axis: {a / 1000:.3f} km\n"
            f"Eccentricity: {e:.5f}"
        ))

    tk.Button(frame, text="Draw Orbit", command=calculate).pack(pady=6)

def calculate_orbit_from_apsides(mu, body_radius, periapsis_km, apoapsis_km):
    """Return two-body orbital parameters from periapsis and apoapsis altitudes."""
    if periapsis_km < 0 or apoapsis_km < 0:
        raise ValueError("Altitudes must be at or above the body's surface.")
    if apoapsis_km < periapsis_km:
        raise ValueError("Apoapsis altitude must be at least the periapsis altitude.")

    r_p = body_radius + periapsis_km * 1000
    r_a = body_radius + apoapsis_km * 1000
    semi_major_axis = (r_p + r_a) / 2
    eccentricity = (r_a - r_p) / (r_a + r_p)
    periapsis_velocity = math.sqrt(mu * (2 / r_p - 1 / semi_major_axis))
    apoapsis_velocity = math.sqrt(mu * (2 / r_a - 1 / semi_major_axis))

    return {
        "type": "Elliptic",
        "periapsis_altitude": periapsis_km,
        "apoapsis_altitude": apoapsis_km,
        "r_p": r_p,
        "r_a": r_a,
        "a": semi_major_axis,
        "e": eccentricity,
        "p": semi_major_axis * (1 - eccentricity ** 2),
        "v_p": periapsis_velocity,
        "v_a": apoapsis_velocity,
        "period": 2 * math.pi * math.sqrt(semi_major_axis ** 3 / mu),
        "escape_velocity": math.sqrt(2 * mu / r_p),
        "display_radius": r_a,
    }


def calculate_orbit_from_periapsis_velocity(mu, body_radius, periapsis_km, velocity_kms):
    """Return two-body orbital parameters when the supplied point is periapsis."""
    if periapsis_km < 0:
        raise ValueError("Periapsis altitude must be at or above the body's surface.")
    if velocity_kms <= 0:
        raise ValueError("Velocity must be greater than zero.")

    r_p = body_radius + periapsis_km * 1000
    v_p = velocity_kms * 1000
    circular_velocity = math.sqrt(mu / r_p)
    escape_velocity = math.sqrt(2 * mu / r_p)
    tolerance = 1e-9 * escape_velocity

    if v_p < circular_velocity - tolerance:
        raise ValueError("Velocity at periapsis must be at least the circular velocity.")

    eccentricity = r_p * v_p ** 2 / mu - 1

    if abs(v_p - escape_velocity) <= tolerance:
        return {
            "type": "Parabolic",
            "periapsis_altitude": periapsis_km,
            "apoapsis_altitude": None,
            "r_p": r_p,
            "r_a": None,
            "a": None,
            "e": 1.0,
            "p": 2 * r_p,
            "v_p": v_p,
            "v_a": None,
            "period": None,
            "escape_velocity": escape_velocity,
            "display_radius": r_p * 8,
        }

    semi_major_axis = r_p / (1 - eccentricity)
    if eccentricity < 1:
        r_a = semi_major_axis * (1 + eccentricity)
        return {
            "type": "Elliptic",
            "periapsis_altitude": periapsis_km,
            "apoapsis_altitude": (r_a - body_radius) / 1000,
            "r_p": r_p,
            "r_a": r_a,
            "a": semi_major_axis,
            "e": eccentricity,
            "p": semi_major_axis * (1 - eccentricity ** 2),
            "v_p": v_p,
            "v_a": math.sqrt(mu * (2 / r_a - 1 / semi_major_axis)),
            "period": 2 * math.pi * math.sqrt(semi_major_axis ** 3 / mu),
            "escape_velocity": escape_velocity,
            "display_radius": r_a,
        }

    return {
        "type": "Hyperbolic",
        "periapsis_altitude": periapsis_km,
        "apoapsis_altitude": None,
        "r_p": r_p,
        "r_a": None,
        "a": semi_major_axis,
        "e": eccentricity,
        "p": semi_major_axis * (1 - eccentricity ** 2),
        "v_p": v_p,
        "v_a": None,
        "period": None,
        "escape_velocity": escape_velocity,
        "v_infinity": math.sqrt(v_p ** 2 - escape_velocity ** 2),
        "display_radius": r_p * 8,
    }


def draw_orbit_trajectory(canvas, orbit, scale, cx, cy):
    """Draw a conic safely, including bounded views of escape trajectories."""
    eccentricity = orbit["e"]
    semi_latus_rectum = orbit["p"]
    max_radius = orbit["display_radius"]

    if orbit["type"] == "Elliptic":
        theta_min, theta_max = 0.0, 2 * math.pi
    else:
        cosine_limit = (semi_latus_rectum / max_radius - 1) / eccentricity
        cosine_limit = max(-1.0, min(1.0, cosine_limit))
        theta_max = math.acos(cosine_limit)
        theta_min = -theta_max

    points = []
    steps = 600
    for index in range(steps + 1):
        theta = theta_min + (theta_max - theta_min) * index / steps
        denominator = 1 + eccentricity * math.cos(theta)
        if denominator <= 0:
            continue

        radius = semi_latus_rectum / denominator
        if radius <= 0 or radius > max_radius * 1.001:
            continue

        points.extend((
            cx + radius * math.cos(theta) * scale,
            cy - radius * math.sin(theta) * scale,
        ))

    if len(points) > 4:
        canvas.create_line(
            points,
            fill="white",
            width=2,
            smooth=True,
            dash=(6, 4) if orbit["type"] != "Elliptic" else None,
        )


def format_orbit_results(orbit):
    """Format values for the Orbit Visualizer results panel."""
    lines = [
        f"Orbit type: {orbit['type']}",
        f"Eccentricity: {orbit['e']:.6f}",
        f"Periapsis altitude: {orbit['periapsis_altitude']:.3f} km",
        f"Periapsis velocity: {orbit['v_p'] / 1000:.4f} km/s",
        f"Escape velocity at periapsis: {orbit['escape_velocity'] / 1000:.4f} km/s",
    ]

    if orbit["type"] == "Elliptic":
        lines.extend((
            f"Apoapsis altitude: {orbit['apoapsis_altitude']:.3f} km",
            f"Semi-major axis: {orbit['a'] / 1000:.3f} km",
            f"Apoapsis velocity: {orbit['v_a'] / 1000:.4f} km/s",
            f"Orbital period: {orbit['period'] / 60:.2f} min",
        ))
    elif orbit["type"] == "Parabolic":
        lines.append("Trajectory: escape threshold (no orbital period)")
    else:
        lines.extend((
            f"Semi-major axis: {orbit['a'] / 1000:.3f} km",
            f"Hyperbolic excess velocity: {orbit['v_infinity'] / 1000:.4f} km/s",
            "Trajectory: unbound (no orbital period)",
        ))

    return "\n".join(lines)


def format_orbit_summary(orbit):
    """Return the compact result view shown below the orbit canvas."""
    summary = [
        f"Orbit: {orbit['type']}",
        f"Eccentricity: {orbit['e']:.6f}",
    ]
    if orbit["type"] == "Elliptic":
        summary.extend((
            f"Semi-major axis: {orbit['a'] / 1000:.3f} km",
            f"Period: {orbit['period'] / 60:.2f} min",
        ))
    elif orbit["type"] == "Parabolic":
        summary.append("Escape threshold")
    else:
        summary.append(f"v∞: {orbit['v_infinity'] / 1000:.4f} km/s")

    return "   •   ".join(summary)


def orbit_visualizer_UI3(root):
    """Build the first-pass tab-native Orbit Visualizer."""
    bodies = {
        "Earth": {
            "mu": 3.986004418e14,
            "radius": 6.371e6,
            "reference_mode": "earth_moon",
            "color": "#2B6FFF",
        },
        "Sun": {
            "mu": 1.32712440018e20,
            "radius": 6.9634e8,
            "reference_mode": "solar",
            "color": "#FFD54A",
        },
    }

    selected_body = tk.StringVar(value="Earth")
    input_mode = tk.StringVar(value="apsides")
    show_reference = tk.BooleanVar(value=True)
    result_summary = tk.StringVar(value="Enter orbit parameters, then calculate the trajectory.")
    result_details = tk.StringVar(value="")
    details_visible = tk.BooleanVar(value=False)
    current = {"orbit": None, "body": None}
    resize_job = [None]

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    page = ttk.Frame(root)
    page.grid(sticky="nsew")
    page.columnconfigure(0, weight=0)
    page.columnconfigure(1, weight=1)
    page.rowconfigure(0, weight=1)

    setup = ttk.LabelFrame(page, text="Orbit setup", padding=16)
    setup.grid(row=0, column=0, sticky="nsw", padx=(0, 16))
    view = ttk.LabelFrame(page, text="Orbit view", padding=12)
    view.grid(row=0, column=1, sticky="nsew")

    ttk.Label(setup, text="Central body:").grid(row=0, column=0, sticky="w")
    body_box = ttk.Combobox(
        setup,
        textvariable=selected_body,
        values=tuple(bodies),
        state="readonly",
        width=18,
    )
    body_box.grid(row=1, column=0, sticky="ew", pady=(4, 16))

    ttk.Label(setup, text="Input mode:").grid(row=2, column=0, sticky="w")
    ttk.Radiobutton(
        setup,
        text="Apoapsis / periapsis",
        variable=input_mode,
        value="apsides",
    ).grid(row=3, column=0, sticky="w", pady=(4, 2))
    ttk.Radiobutton(
        setup,
        text="Velocity at periapsis",
        variable=input_mode,
        value="velocity",
    ).grid(row=4, column=0, sticky="w", pady=(0, 16))

    ttk.Label(setup, text="Periapsis altitude [km]:").grid(row=5, column=0, sticky="w")
    peri_entry = ttk.Entry(setup, width=22)
    peri_entry.grid(row=6, column=0, sticky="ew", pady=(4, 12))

    ttk.Label(setup, text="Apoapsis altitude [km]:").grid(row=7, column=0, sticky="w")
    apo_entry = ttk.Entry(setup, width=22)
    apo_entry.grid(row=8, column=0, sticky="ew", pady=(4, 12))

    ttk.Label(setup, text="Velocity at periapsis [km/s]:").grid(row=9, column=0, sticky="w")
    velocity_entry = ttk.Entry(setup, width=22)
    velocity_entry.grid(row=10, column=0, sticky="ew", pady=(4, 16))

    canvas = tk.Canvas(view, width=360, height=360, bg="black", highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")
    view.columnconfigure(0, weight=1)
    view.rowconfigure(0, weight=1)
    ttk.Checkbutton(
        view,
        text="Show reference orbits",
        variable=show_reference,
        command=lambda: render_orbit(),
    ).grid(row=1, column=0, sticky="w", pady=(10, 0))
    ttk.Label(
        view,
        text="White: selected orbit   •   Grey: reference orbits",
    ).grid(row=2, column=0, sticky="w", pady=(4, 0))

    result_card = ttk.LabelFrame(view, text="Results", padding=10)
    result_card.grid(row=3, column=0, sticky="ew", pady=(12, 0))
    result_card.columnconfigure(0, weight=1)
    ttk.Label(result_card, textvariable=result_summary, justify=tk.LEFT, wraplength=520).grid(
        row=0, column=0, sticky="w"
    )
    details_button = ttk.Button(result_card, text="Show detailed results")
    details_button.grid(row=1, column=0, sticky="w", pady=(8, 0))
    details_frame = ttk.Frame(result_card)
    ttk.Label(details_frame, textvariable=result_details, justify=tk.LEFT).grid(sticky="w")
    details_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
    details_frame.grid_remove()

    def toggle_details():
        if details_visible.get():
            details_frame.grid_remove()
            details_button.config(text="Show detailed results")
            details_visible.set(False)
        else:
            details_frame.grid()
            details_button.config(text="Hide detailed results")
            details_visible.set(True)

    details_button.config(command=toggle_details)

    def update_mode(*_):
        if input_mode.get() == "apsides":
            apo_entry.state(["!disabled"])
            velocity_entry.state(["disabled"])
        else:
            apo_entry.state(["disabled"])
            velocity_entry.state(["!disabled"])

    def render_orbit():
        resize_job[0] = None
        orbit = current["orbit"]
        body = current["body"]
        if orbit is None or body is None:
            return

        width = max(canvas.winfo_width(), 1)
        height = max(canvas.winfo_height(), 1)
        canvas_size = min(width, height)
        center_x = width / 2
        center_y = height / 2
        scale = compute_orbit_scale(canvas_size, [orbit["display_radius"]], padding=35)

        canvas.delete("all")
        draw_central_body(canvas, center_x, center_y, body["radius"], scale, body["color"])
        if show_reference.get():
            draw_reference_orbits(canvas, body["reference_mode"], scale, center_x, center_y)
        draw_orbit_trajectory(canvas, orbit, scale, center_x, center_y)

    def queue_resize_redraw(_event):
        if current["orbit"] is None:
            return
        if resize_job[0] is not None:
            canvas.after_cancel(resize_job[0])
        resize_job[0] = canvas.after(60, render_orbit)

    def draw_orbit():
        try:
            periapsis_km = float(peri_entry.get())
            body = bodies[selected_body.get()]
            if input_mode.get() == "apsides":
                orbit = calculate_orbit_from_apsides(
                    body["mu"], body["radius"], periapsis_km, float(apo_entry.get())
                )
            else:
                orbit = calculate_orbit_from_periapsis_velocity(
                    body["mu"], body["radius"], periapsis_km, float(velocity_entry.get())
                )
        except ValueError as error:
            result_summary.set(f"Error: {error}")
            result_details.set("")
            return

        current["orbit"] = orbit
        current["body"] = body
        result_summary.set(format_orbit_summary(orbit))
        result_details.set(format_orbit_results(orbit))
        render_orbit()

    def reset():
        selected_body.set("Earth")
        input_mode.set("apsides")
        show_reference.set(True)
        for entry in (peri_entry, apo_entry, velocity_entry):
            entry.delete(0, tk.END)
        canvas.delete("all")
        current["orbit"] = None
        current["body"] = None
        result_summary.set("Enter orbit parameters, then calculate the trajectory.")
        result_details.set("")
        if details_visible.get():
            toggle_details()
        update_mode()
        peri_entry.focus()

    button_row = ttk.Frame(setup)
    button_row.grid(row=11, column=0, sticky="ew")
    ttk.Button(button_row, text="Calculate & Draw Orbit", command=draw_orbit).pack(side=tk.LEFT)
    ttk.Button(button_row, text="Reset", command=reset).pack(side=tk.LEFT, padx=(8, 0))

    input_mode.trace_add("write", update_mode)
    canvas.bind("<Configure>", queue_resize_redraw)
    for entry in (peri_entry, apo_entry, velocity_entry):
        entry.bind("<Return>", lambda _event: draw_orbit())
    update_mode()
    peri_entry.focus()



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

        if ro <= 0:
            result_label.config(text="Error: Parallax must be greater than 0 arcseconds.")
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
            wavelength = float(wavelengthi)
            if wavelength <= 0:
                raise ValueError
        except ValueError:
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

        if temp <= 0:
            result_label.config(text="Error: Temperature must be greater than 0 K.")
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
