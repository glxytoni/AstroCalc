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

def draw_reference_orbits(canvas, mode, scale, cx, cy, clip_to_view=False):
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
            if clip_to_view and r * scale > math.hypot(
                max(abs(cx), abs(canvas.winfo_width() - cx)),
                max(abs(cy), abs(canvas.winfo_height() - cy)),
            ) + 2:
                continue
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
def calculate_hohmann_transfer(mu, body_radius, start_km, target_km):
    """Ideal coplanar circular transfer; SI results and signed tangential burns."""
    if not all(math.isfinite(v) for v in (mu, body_radius, start_km, target_km)):
        raise ValueError("Enter finite numbers.")
    if mu <= 0 or body_radius <= 0 or start_km < 0 or target_km < 0:
        raise ValueError("Altitudes must be at or above the body's surface.")
    r1 = body_radius + start_km * 1000
    r2 = body_radius + target_km * 1000
    a = r1 / 2 + r2 / 2
    v1, v2 = math.sqrt(mu / r1), math.sqrt(mu / r2)
    vt1 = v1 * math.sqrt(r2 / a)
    vt2 = v2 * math.sqrt(r1 / a)
    no_transfer = r1 == r2
    dv1 = 0.0 if no_transfer else vt1 - v1
    dv2 = 0.0 if no_transfer else v2 - vt2
    coast = 0.0 if no_transfer else math.pi * a * math.sqrt(a / mu)
    if not all(math.isfinite(v) for v in (r1, r2, a, v1, v2, vt1, vt2, coast)):
        raise ValueError("Values exceed the supported numeric range.")
    direction = "None" if no_transfer else ("Prograde" if r2 > r1 else "Retrograde")
    return {
        "r1": r1, "r2": r2, "a": a, "b": math.sqrt(r1) * math.sqrt(r2),
        "e": abs(r2 / a - r1 / a) / 2,
        "v1": v1, "v2": v2, "vt1": vt1, "vt2": vt2,
        "dv1": dv1, "dv2": dv2, "total_dv": abs(dv1) + abs(dv2),
        "coast": coast, "direction": direction, "no_transfer": no_transfer,
    }


def hohmann_transfer_arc(transfer, steps=400):
    """Travelled upper half-ellipse, from (+r1, 0) to (-r2, 0).

    The signed centre offset places departure at apoapsis for inward transfers.
    Coordinates are in metres with the central body at the origin.
    """
    if transfer["no_transfer"]:
        return []
    offset = (transfer["r1"] - transfer["r2"]) / 2
    points = [
        (offset + transfer["a"] * math.cos(math.pi * i / steps),
         transfer["b"] * math.sin(math.pi * i / steps))
        for i in range(steps + 1)
    ]
    points[0] = (transfer["r1"], 0.0)
    points[-1] = (-transfer["r2"], 0.0)
    return points


def hohmann_transfer_UI4(root):
    """Scrollable Hohmann calculator with a zoomable transfer view."""
    for widget in root.winfo_children():
        widget.destroy()

    style = ttk.Style(root)
    style.configure("Hohmann.Value.TLabel", font=("TkDefaultFont", 16, "bold"))
    style.configure("Hohmann.Error.TLabel", foreground="#a12622")
    selected_body = tk.StringVar(master=root, value="Earth")
    error_text = tk.StringVar(master=root)
    detail_text = tk.StringVar(master=root)
    zoom_text = tk.StringVar(master=root, value="100%")
    values = {key: tk.StringVar(master=root, value="—")
              for key in ("total", "time", "departure", "arrival")}
    current = {"transfer": None, "body": None}
    camera = {"zoom": 1.0, "x": 0.0, "y": 0.0, "drag": None}
    redraw_job = [None]

    shell = ttk.Frame(root)
    shell.pack(fill=tk.BOTH, expand=True)
    shell.columnconfigure(0, weight=1)
    shell.rowconfigure(0, weight=1)
    viewport = tk.Canvas(shell, width=1, height=1, highlightthickness=0,
                         background=style.lookup("TFrame", "background") or "#eeeeee")
    viewport.grid(row=0, column=0, sticky="nsew")
    scroll = ttk.Scrollbar(shell, orient="vertical", command=viewport.yview)
    scroll.grid(row=0, column=1, sticky="ns")
    viewport.configure(yscrollcommand=scroll.set)
    page = ttk.Frame(viewport, padding=(4, 4, 16, 16))
    page.columnconfigure(0, weight=1)
    page_item = viewport.create_window(0, 0, window=page, anchor="nw")
    page.bind("<Configure>", lambda _e: viewport.configure(scrollregion=viewport.bbox("all")))

    def wrap_label(parent, **options):
        label = ttk.Label(parent, width=1, wraplength=1, justify=tk.LEFT, **options)

        def fit_text(event):
            width = max(1, event.width - 4)
            if int(label.cget("wraplength")) != width:
                label.configure(wraplength=width)

        label.bind("<Configure>", fit_text)
        return label

    wrap_label(page, text="Transfer between two circular orbits around the same body.").grid(
        row=0, column=0, sticky="ew", pady=(0, 16))
    top = ttk.Frame(page)
    top.grid(row=1, column=0, sticky="ew")
    top.columnconfigure(1, weight=1)
    inputs = ttk.LabelFrame(top, text="Inputs", padding=16)
    inputs.grid(row=0, column=0, sticky="new", padx=(0, 16))
    inputs.columnconfigure(0, weight=1)
    view = ttk.LabelFrame(top, text="Transfer view", padding=12)
    view.grid(row=0, column=1, sticky="nsew")
    view.columnconfigure(0, weight=1)

    def resize_page(event):
        viewport.itemconfigure(page_item, width=max(1, event.width))
        if event.width < 700:
            top.columnconfigure(0, weight=1)
            top.columnconfigure(1, weight=0)
            inputs.grid_configure(row=0, column=0, padx=0, pady=(0, 16), sticky="ew")
            view.grid_configure(row=1, column=0, sticky="ew")
        else:
            top.columnconfigure(0, weight=0)
            top.columnconfigure(1, weight=1)
            inputs.grid_configure(row=0, column=0, padx=(0, 16), pady=0, sticky="new")
            view.grid_configure(row=0, column=1, sticky="nsew")

    viewport.bind("<Configure>", resize_page)
    ttk.Label(inputs, text="Central body").grid(row=0, column=0, sticky="w")
    body_box = ttk.Combobox(inputs, textvariable=selected_body, state="readonly", width=18,
                           values=tuple(key.title() for key in SOLAR_SYSTEM))
    body_box.grid(row=1, column=0, sticky="ew", pady=(4, 16))

    def altitude_field(row, title):
        ttk.Label(inputs, text=title).grid(row=row, column=0, sticky="w")
        field = ttk.Frame(inputs)
        field.grid(row=row + 1, column=0, sticky="ew", pady=(4, 12))
        field.columnconfigure(0, weight=1)
        entry = ttk.Entry(field, width=16)
        entry.grid(row=0, column=0, sticky="ew")
        ttk.Label(field, text="km").grid(row=0, column=1, padx=(8, 0))
        return entry

    start_alt_entry = altitude_field(2, "Start altitude")
    final_alt_entry = altitude_field(4, "Target altitude")
    actions = ttk.Frame(inputs)
    actions.grid(row=6, column=0, sticky="w", pady=(8, 0))
    error_label = wrap_label(inputs, textvariable=error_text, style="Hohmann.Error.TLabel")
    error_label.grid(row=7, column=0, sticky="ew", pady=(8, 0))
    error_label.grid_remove()

    canvas = tk.Canvas(view, width=1, height=340, bg="#101822", highlightthickness=0, cursor="hand2")
    canvas.grid(row=0, column=0, sticky="ew")
    navigation = ttk.Frame(view)
    navigation.grid(row=1, column=0, sticky="w", pady=(8, 0))
    wrap_label(view, text="Wheel: zoom • Drag: pan\nGrey: circular orbits • Cyan: travelled arc\nCyan marker: departure • Orange marker: arrival").grid(
        row=2, column=0, sticky="ew", pady=(8, 0))

    results = ttk.LabelFrame(page, text="Results", padding=16)
    results.grid(row=2, column=0, sticky="ew", pady=(16, 0))
    results.columnconfigure(1, weight=1)
    for row, (key, title) in enumerate((
        ("total", "Total ΔV"), ("time", "Transfer time"),
        ("departure", "Departure burn"), ("arrival", "Arrival burn"),
    )):
        ttk.Label(results, text=title).grid(row=row, column=0, sticky="nw", padx=(0, 16), pady=6)
        wrap_label(results, textvariable=values[key],
                   style="Hohmann.Value.TLabel" if row < 2 else "TLabel").grid(
            row=row, column=1, sticky="ew", pady=6)
    details_button = ttk.Button(results, text="Show details ▾", state="disabled")
    details_button.grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 0))
    details = ttk.Frame(results)
    details.columnconfigure(0, weight=1)
    wrap_label(details, textvariable=detail_text).grid(row=0, column=0, sticky="ew")
    details.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 0))
    details.grid_remove()

    def hide_details():
        details.grid_remove()
        details_button.configure(text="Show details ▾")

    def toggle_details():
        if details.winfo_manager():
            hide_details()
        else:
            details.grid()
            details_button.configure(text="Hide details ▴")

    details_button.configure(command=toggle_details)

    def cancel_redraw():
        if redraw_job[0] is not None:
            canvas.after_cancel(redraw_job[0])
            redraw_job[0] = None

    def transform():
        w, h = max(1, canvas.winfo_width()), max(1, canvas.winfo_height())
        extent = max(current["transfer"]["r1"], current["transfer"]["r2"])
        size = min(w, h)
        scale = (size / 2 - min(40, size * 0.12)) / extent * camera["zoom"]
        return w, h, scale

    def render():
        cancel_redraw()
        canvas.delete("all")
        transfer, body = current["transfer"], current["body"]
        if transfer is None:
            return
        w, h, scale = transform()
        cx, cy = w / 2 - camera["x"] * scale, h / 2 + camera["y"] * scale
        radius = max(3, body["radius"] * scale)
        canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius,
                           fill=body["color"], outline="", tags="body")
        farthest = math.hypot(max(abs(cx), abs(w-cx)), max(abs(cy), abs(h-cy)))
        for key, dash in (("r1", ()), ("r2", (5, 4))):
            if key == "r2" and transfer["no_transfer"]:
                continue
            r = transfer[key] * scale
            if r <= farthest + 2:
                canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#81909d",
                                   dash=dash, tags=key)
        points = hohmann_transfer_arc(transfer)
        if points:
            pixels = [(cx + x * scale, cy - y * scale) for x, y in points]
            canvas.create_line([v for point in pixels for v in point],
                               fill="#66d9ef", width=3, tags="transfer_arc")
            mid = len(pixels) // 2
            canvas.create_line(*pixels[mid-4], *pixels[mid+4],
                               fill="#66d9ef", width=3, arrow=tk.LAST,
                               arrowshape=(12, 14, 5), tags="travel_arrow")
        markers = [(transfer["r1"], "Departure", "#66d9ef")]
        if transfer["no_transfer"]:
            markers = [(transfer["r1"], "Shared orbit", "#66d9ef")]
        else:
            markers.append((-transfer["r2"], "Arrival", "#ffbf69"))
        for x, title, color in markers:
            px = cx + x * scale
            canvas.create_oval(px-5, cy-5, px+5, cy+5, fill=color, outline="", tags="marker")
            canvas.create_text(px, cy+12, text=title, fill=color, anchor="n",
                               font=("TkDefaultFont", 10), tags="marker_label")

    def fit_orbit():
        camera.update(zoom=1.0, x=0.0, y=0.0, drag=None)
        canvas.configure(cursor="hand2")
        zoom_text.set("100%")
        render()

    def zoom_at(factor, x=None, y=None):
        if current["transfer"] is None:
            return
        w, h, old_scale = transform()
        x, y = w / 2 if x is None else x, h / 2 if y is None else y
        zoom = max(0.01, min(100, camera["zoom"] * factor))
        new_scale = old_scale * zoom / camera["zoom"]
        camera["x"] += (x-w/2) * (1/old_scale-1/new_scale)
        camera["y"] -= (y-h/2) * (1/old_scale-1/new_scale)
        camera["zoom"] = zoom
        zoom_text.set(f"{zoom*100:.0f}%")
        render()

    def wheel_zoom(event):
        number, delta = getattr(event, "num", None), getattr(event, "delta", 0)
        if number in (4, 5):
            steps = 1 if number == 4 else -1
        elif delta:
            steps = max(-4, min(4, delta/120 if abs(delta) >= 120 else (1 if delta > 0 else -1)))
        else:
            return "break"
        zoom_at(1.25 ** steps, event.x, event.y)
        return "break"

    def start_pan(event):
        if current["transfer"] is not None:
            camera["drag"] = (event.x, event.y)
            canvas.configure(cursor="fleur")

    def pan(event):
        if camera["drag"] is None or current["transfer"] is None:
            return
        _, _, scale = transform()
        oldx, oldy = camera["drag"]
        camera["x"] -= (event.x-oldx) / scale
        camera["y"] += (event.y-oldy) / scale
        camera["drag"] = (event.x, event.y)
        render()

    def end_pan(_event=None):
        camera["drag"] = None
        canvas.configure(cursor="hand2")

    def resize_drawing(event):
        desired = max(260, min(440, int(event.width * 0.85)))
        if int(canvas.cget("height")) != desired:
            canvas.configure(height=desired)
        cancel_redraw()
        redraw_job[0] = canvas.after(60, render)

    def clear_results():
        for variable in values.values():
            variable.set("—")
        detail_text.set("")
        hide_details()
        details_button.state(["disabled"])
        current.update(transfer=None, body=None)
        end_pan()
        fit_orbit()

    def calculate(*_):
        try:
            start_km, target_km = float(start_alt_entry.get()), float(final_alt_entry.get())
            body = SOLAR_SYSTEM[selected_body.get().lower()]
            transfer = calculate_hohmann_transfer(G * body["mass"], body["radius"], start_km, target_km)
        except (ValueError, OverflowError, ZeroDivisionError) as error:
            clear_results()
            error_text.set(f"Check altitudes: {error}")
            error_label.grid()
            return
        error_text.set("")
        error_label.grid_remove()
        current.update(transfer=transfer, body=body)
        values["total"].set(f"{transfer['total_dv']/1000:,.3f} km/s")
        if transfer["no_transfer"]:
            values["time"].set("No transfer needed")
        else:
            seconds = round(transfer["coast"])
            days, seconds = divmod(seconds, 86400)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)
            duration = f"{hours} h {minutes:02d} min {seconds:02d} s"
            values["time"].set((f"{days} d " if days else "") + duration)
        for key, dv in (("departure", transfer["dv1"]), ("arrival", transfer["dv2"])):
            values[key].set("No burn needed" if transfer["no_transfer"] else
                            f"{abs(dv)/1000:,.3f} km/s · {transfer['direction']}")
        detail_text.set(
            f"Central body: {selected_body.get()}\n"
            f"Start / target altitude: {start_km:g} / {target_km:g} km\n"
            f"Start / target radius: {transfer['r1']/1000:,.3f} / {transfer['r2']/1000:,.3f} km\n\n"
            f"Initial / final circular speed: {transfer['v1']/1000:.6f} / {transfer['v2']/1000:.6f} km/s\n"
            f"Transfer speed at departure / arrival: {transfer['vt1']/1000:.6f} / {transfer['vt2']/1000:.6f} km/s\n"
            f"Semi-major axis: {transfer['a']/1000:,.3f} km\n"
            f"Eccentricity: {transfer['e']:.6f}\n"
            f"Coast time: {transfer['coast']:,.3f} s\n\n"
            "Prograde adds speed along the motion; retrograde reduces it.\n"
            "Ideal two-body model: coplanar circular orbits and instantaneous tangential burns.\n"
            "Transfer time is the coast between burns; launch, phasing, and burn duration are excluded."
        )
        details_button.state(["!disabled"])
        fit_orbit()

    def reset():
        selected_body.set("Earth")
        for entry in (start_alt_entry, final_alt_entry):
            entry.delete(0, tk.END)
        error_text.set("")
        error_label.grid_remove()
        clear_results()
        viewport.yview_moveto(0)
        start_alt_entry.focus_set()

    ttk.Button(actions, text="Calculate", command=calculate).pack(side=tk.LEFT)
    ttk.Button(actions, text="Reset", command=reset).pack(side=tk.LEFT, padx=(8, 0))
    ttk.Button(navigation, text="−", width=3, command=lambda: zoom_at(1/1.25)).pack(side=tk.LEFT)
    ttk.Button(navigation, text="+", width=3, command=lambda: zoom_at(1.25)).pack(side=tk.LEFT, padx=4)
    ttk.Button(navigation, text="Fit orbit", command=fit_orbit).pack(side=tk.LEFT)
    ttk.Label(navigation, textvariable=zoom_text).pack(side=tk.LEFT, padx=8)
    for entry in (start_alt_entry, final_alt_entry):
        entry.bind("<Return>", calculate)

    def scroll_page(event):
        if viewport.yview() != (0.0, 1.0):
            up = getattr(event, "delta", 0) > 0 or getattr(event, "num", None) == 4
            viewport.yview_scroll(-3 if up else 3, "units")
            return "break"

    def bind_scrolling(widget):
        if widget is canvas:
            return  # The wheel over the drawing belongs to zoom, not page scrolling.
        for event_name in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            widget.bind(event_name, scroll_page, add="+")
        for child in widget.winfo_children():
            bind_scrolling(child)

    bind_scrolling(viewport)
    for event_name in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
        canvas.bind(event_name, wheel_zoom)
    canvas.bind("<ButtonPress-1>", start_pan)
    canvas.bind("<B1-Motion>", pan)
    canvas.bind("<ButtonRelease-1>", end_pan)
    canvas.bind("<Configure>", resize_drawing)
    canvas.bind("<Destroy>", lambda _event: cancel_redraw())
    start_alt_entry.focus_set()


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


def draw_orbit_trajectory(canvas, orbit, scale, cx, cy, view_radius=None):
    """Draw a conic safely, including bounded views of escape trajectories."""
    eccentricity = orbit["e"]
    semi_latus_rectum = orbit["p"]
    max_radius = max(orbit["r_p"], view_radius or orbit["display_radius"])
    points = []
    steps = 800
    # Anomaly-based sampling remains smooth along escape trajectories when zoomed out.
    if orbit["type"] == "Parabolic":
        limit = math.sqrt(max(0, max_radius / orbit["r_p"] - 1))
    elif orbit["type"] == "Hyperbolic":
        axis = abs(orbit["a"])
        limit = math.acosh(max(1, (max_radius / axis + 1) / eccentricity))

    for index in range(steps + 1):
        fraction = index / steps
        if orbit["type"] == "Elliptic":
            anomaly = 2 * math.pi * fraction
            x = orbit["a"] * (math.cos(anomaly) - eccentricity)
            y = math.sqrt(orbit["a"] * semi_latus_rectum) * math.sin(anomaly)
        elif orbit["type"] == "Parabolic":
            anomaly = (2 * fraction - 1) * limit
            x = orbit["r_p"] * (1 - anomaly * anomaly)
            y = 2 * orbit["r_p"] * anomaly
        else:
            anomaly = (2 * fraction - 1) * limit
            x = axis * (eccentricity - math.cosh(anomaly))
            y = math.sqrt(axis * semi_latus_rectum) * math.sinh(anomaly)
        points.extend((cx + x * scale, cy - y * scale))

    if len(points) > 4:
        canvas.create_line(
            points,
            fill="white",
            width=2,
            smooth=False,
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
    details_visible = tk.BooleanVar(value=False)
    current = {"orbit": None, "body": None}
    resize_job = [None]
    camera = {"zoom": 1.0, "x": 0.0, "y": 0.0, "drag": None}
    zoom_text = tk.StringVar(master=root, value="100%")

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

    ttk.Label(setup, text="Input mode:").grid(row=3, column=0, sticky="w")
    ttk.Radiobutton(
        setup,
        text="Apoapsis / periapsis",
        variable=input_mode,
        value="apsides",
    ).grid(row=4, column=0, sticky="w", pady=(4, 2))
    ttk.Radiobutton(
        setup,
        text="Velocity at periapsis",
        variable=input_mode,
        value="velocity",
    ).grid(row=5, column=0, sticky="w", pady=(0, 16))

    ttk.Label(setup, text="Periapsis altitude [km]:").grid(row=6, column=0, sticky="w")
    peri_entry = ttk.Entry(setup, width=22)
    peri_entry.grid(row=7, column=0, sticky="ew", pady=(4, 12))

    apo_label = ttk.Label(setup, text="Apoapsis altitude [km]:")
    apo_label.grid(row=8, column=0, sticky="w")
    apo_entry = ttk.Entry(setup, width=22)
    apo_entry.grid(row=9, column=0, sticky="ew", pady=(4, 12))

    velocity_label = ttk.Label(setup, text="Velocity at periapsis [km/s]:")
    velocity_label.grid(row=8, column=0, sticky="w")
    velocity_entry = ttk.Entry(setup, width=22)
    velocity_entry.grid(row=9, column=0, sticky="ew", pady=(4, 12))

    canvas = tk.Canvas(view, width=360, height=360, bg="black", highlightthickness=0, cursor="hand2")
    canvas.grid(row=0, column=0, sticky="nsew")
    view.columnconfigure(0, weight=1)
    view.rowconfigure(0, weight=1)
    navigation = ttk.Frame(view)
    navigation.grid(row=1, column=0, sticky="ew", pady=(8, 0))
    ttk.Button(navigation, text="−", width=3, command=lambda: zoom_at(1 / 1.25)).pack(side=tk.LEFT)
    ttk.Button(navigation, text="+", width=3, command=lambda: zoom_at(1.25)).pack(side=tk.LEFT, padx=4)
    ttk.Button(navigation, text="Fit orbit", command=lambda: fit_orbit()).pack(side=tk.LEFT)
    ttk.Label(navigation, textvariable=zoom_text).pack(side=tk.LEFT, padx=8)
    ttk.Checkbutton(
        view,
        text="Show reference orbits",
        variable=show_reference,
        command=lambda: render_orbit(),
    ).grid(row=2, column=0, sticky="w", pady=(10, 0))
    legend_label = ttk.Label(
        view,
        text="Wheel: zoom • Drag: pan\nWhite: orbit • Grey: references",
        width=1, wraplength=1, justify=tk.LEFT,
    )
    legend_label.grid(row=3, column=0, sticky="ew", pady=(4, 0))

    result_card = ttk.LabelFrame(view, text="Results", padding=10)
    result_card.grid(row=4, column=0, sticky="ew", pady=(12, 0))
    result_card.columnconfigure(0, weight=1)
    summary_label = ttk.Label(
        result_card, textvariable=result_summary, justify=tk.LEFT,
        width=1, wraplength=1,
    )
    summary_label.grid(row=0, column=0, sticky="ew")

    def fit_text_to_width(event):
        # Use the allocated label width, including when the tab is narrowed.
        wraplength = max(1, event.width - 4)
        if int(event.widget.cget("wraplength")) != wraplength:
            event.widget.configure(wraplength=wraplength)

    legend_label.bind("<Configure>", fit_text_to_width)
    summary_label.bind("<Configure>", fit_text_to_width)
    details_button = ttk.Button(result_card, text="Show detailed results")
    details_button.grid(row=1, column=0, sticky="w", pady=(8, 0))
    details_frame = ttk.Frame(result_card)
    details_frame.columnconfigure(0, weight=1)
    details_text = tk.Text(
        details_frame, height=4, width=1, wrap="word",
        font="TkDefaultFont", state="disabled", padx=6, pady=4,
    )
    details_text.grid(row=0, column=0, sticky="ew")
    details_scrollbar = ttk.Scrollbar(
        details_frame, orient="vertical", command=details_text.yview,
    )
    details_scrollbar.grid(row=0, column=1, sticky="ns")
    details_text.configure(yscrollcommand=details_scrollbar.set)
    details_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
    details_frame.grid_remove()

    def set_details(text):
        details_text.configure(state="normal")
        details_text.delete("1.0", tk.END)
        details_text.insert("1.0", text)
        details_text.yview_moveto(0)
        details_text.configure(state="disabled")

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
        apsides = input_mode.get() == "apsides"
        for widget in (apo_label, apo_entry):
            if apsides:
                widget.grid()
            else:
                widget.grid_remove()
        for widget in (velocity_label, velocity_entry):
            if apsides:
                widget.grid_remove()
            else:
                widget.grid()

    def view_transform():
        width = max(canvas.winfo_width(), 1)
        height = max(canvas.winfo_height(), 1)
        canvas_size = min(width, height)
        padding = min(35, canvas_size * 0.1)
        scale = (canvas_size / 2 - padding) / current["orbit"]["display_radius"]
        scale *= camera["zoom"]
        return width, height, scale

    def cancel_redraw():
        if resize_job[0] is not None:
            canvas.after_cancel(resize_job[0])
            resize_job[0] = None

    def render_orbit():
        cancel_redraw()
        orbit = current["orbit"]
        body = current["body"]
        if orbit is None or body is None:
            return

        width, height, scale = view_transform()
        center_x = width / 2 - camera["x"] * scale
        center_y = height / 2 + camera["y"] * scale
        visible_radius = 1.1 * math.hypot(
            max(abs(center_x), abs(width - center_x)),
            max(abs(center_y), abs(height - center_y)),
        ) / scale

        canvas.delete("all")
        draw_central_body(
            canvas, center_x, center_y, body["radius"], scale, body["color"],
            min_px=3, max_px=max(3, body["radius"] * scale),
        )
        if show_reference.get():
            draw_reference_orbits(
                canvas, body["reference_mode"], scale, center_x, center_y, clip_to_view=True,
            )
        draw_orbit_trajectory(canvas, orbit, scale, center_x, center_y, view_radius=visible_radius)

    def fit_orbit():
        camera.update(zoom=1.0, x=0.0, y=0.0, drag=None)
        zoom_text.set("100%")
        render_orbit()

    def zoom_at(factor, x=None, y=None):
        if current["orbit"] is None:
            return
        width, height, old_scale = view_transform()
        x = width / 2 if x is None else x
        y = height / 2 if y is None else y
        new_zoom = max(0.01, min(100.0, camera["zoom"] * factor))
        new_scale = old_scale * new_zoom / camera["zoom"]
        # Preserve the physical point beneath the cursor while changing scale.
        camera["x"] += (x - width / 2) * (1 / old_scale - 1 / new_scale)
        camera["y"] -= (y - height / 2) * (1 / old_scale - 1 / new_scale)
        camera["zoom"] = new_zoom
        zoom_text.set(f"{new_zoom * 100:.0f}%")
        render_orbit()

    def wheel_zoom(event):
        number = getattr(event, "num", None)
        delta = getattr(event, "delta", 0)
        if number in (4, 5):
            steps = 1 if number == 4 else -1
        elif delta:
            steps = max(-4, min(4, delta / 120 if abs(delta) >= 120 else (1 if delta > 0 else -1)))
        else:
            return "break"
        zoom_at(1.25 ** steps, event.x, event.y)
        return "break"

    def start_pan(event):
        if current["orbit"] is not None:
            camera["drag"] = (event.x, event.y)
            canvas.configure(cursor="fleur")

    def pan(event):
        if camera["drag"] is None or current["orbit"] is None:
            return
        _, _, scale = view_transform()
        previous_x, previous_y = camera["drag"]
        camera["x"] -= (event.x - previous_x) / scale
        camera["y"] += (event.y - previous_y) / scale
        camera["drag"] = (event.x, event.y)
        render_orbit()

    def end_pan(_event=None):
        camera["drag"] = None
        canvas.configure(cursor="hand2")

    def queue_resize_redraw(_event):
        if current["orbit"] is None:
            return
        cancel_redraw()
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
            set_details("")
            return

        current["orbit"] = orbit
        current["body"] = body
        result_summary.set(format_orbit_summary(orbit))
        set_details(format_orbit_results(orbit))
        fit_orbit()

    def reset():
        cancel_redraw()
        end_pan()
        camera.update(zoom=1.0, x=0.0, y=0.0)
        zoom_text.set("100%")
        selected_body.set("Earth")
        input_mode.set("apsides")
        show_reference.set(True)
        for entry in (peri_entry, apo_entry, velocity_entry):
            entry.state(["!disabled"])
            entry.delete(0, tk.END)
        canvas.delete("all")
        current["orbit"] = None
        current["body"] = None
        result_summary.set("Enter orbit parameters, then calculate the trajectory.")
        set_details("")
        if details_visible.get():
            toggle_details()
        update_mode()
        peri_entry.focus()

    button_row = ttk.Frame(setup)
    button_row.grid(row=2, column=0, sticky="ew", pady=(0, 12))
    ttk.Button(button_row, text="Calculate & Draw Orbit", command=draw_orbit).pack(side=tk.LEFT)
    ttk.Button(button_row, text="Reset", command=reset).pack(side=tk.LEFT, padx=(8, 0))

    input_mode.trace_add("write", update_mode)
    canvas.bind("<Configure>", queue_resize_redraw)
    canvas.bind("<MouseWheel>", wheel_zoom)
    canvas.bind("<Button-4>", wheel_zoom)
    canvas.bind("<Button-5>", wheel_zoom)
    canvas.bind("<ButtonPress-1>", start_pan)
    canvas.bind("<B1-Motion>", pan)
    canvas.bind("<ButtonRelease-1>", end_pan)
    canvas.bind("<Destroy>", lambda _event: cancel_redraw())
    for entry in (peri_entry, apo_entry, velocity_entry):
        entry.bind("<Return>", lambda _event: draw_orbit())
    update_mode()
    peri_entry.focus()



def _single_input_calculator_UI(root, description, input_label, unit, result_labels, evaluator, hint,
                                result_visual=None):
    """Shared scrollable card layout for simple one-input calculators."""
    for widget in root.winfo_children():
        widget.destroy()

    style = ttk.Style(root)
    style.configure("SimpleCalc.Value.TLabel", font=("TkDefaultFont", 16, "bold"))
    style.configure("SimpleCalc.Error.TLabel", foreground="#a12622")
    shell = ttk.Frame(root)
    shell.pack(fill=tk.BOTH, expand=True)
    shell.columnconfigure(0, weight=1)
    shell.rowconfigure(0, weight=1)
    viewport = tk.Canvas(
        shell, width=1, height=1, highlightthickness=0,
        background=style.lookup("TFrame", "background") or "#eeeeee",
    )
    viewport.grid(row=0, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(shell, orient="vertical", command=viewport.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    viewport.configure(yscrollcommand=scrollbar.set)
    page = ttk.Frame(viewport, padding=(4, 4, 16, 16))
    page.columnconfigure(0, weight=1)
    page_item = viewport.create_window(0, 0, window=page, anchor="nw")

    def resize_page(event):
        viewport.itemconfigure(page_item, width=max(1, event.width))

    def update_scroll_region(_event=None):
        viewport.configure(scrollregion=viewport.bbox("all"))

    viewport.bind("<Configure>", resize_page)
    page.bind("<Configure>", update_scroll_region)

    def wrapping_label(parent, **options):
        label = ttk.Label(parent, width=1, wraplength=1, justify=tk.LEFT, **options)

        def fit_text(event):
            width = max(1, event.width - 4)
            if int(label.cget("wraplength")) != width:
                label.configure(wraplength=width)

        label.bind("<Configure>", fit_text)
        return label

    wrapping_label(page, text=description).grid(row=0, column=0, sticky="ew", pady=(0, 16))
    inputs = ttk.LabelFrame(page, text="Inputs", padding=16)
    inputs.grid(row=1, column=0, sticky="ew")
    inputs.columnconfigure(1, weight=1)
    ttk.Label(inputs, text=input_label).grid(row=0, column=0, sticky="w", padx=(0, 16))
    entry = ttk.Entry(inputs, width=16)
    entry.grid(row=0, column=1, sticky="ew")
    ttk.Label(inputs, text=unit).grid(row=0, column=2, sticky="w", padx=(8, 0))
    wrapping_label(inputs, text=hint).grid(
        row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0),
    )
    actions = ttk.Frame(inputs)
    actions.grid(row=2, column=0, columnspan=3, sticky="w", pady=(12, 0))
    error_text = tk.StringVar(master=root)
    error_label = wrapping_label(inputs, textvariable=error_text, style="SimpleCalc.Error.TLabel")
    error_label.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(8, 0))
    error_label.grid_remove()

    results = ttk.LabelFrame(page, text="Results", padding=16)
    results.grid(row=2, column=0, sticky="ew", pady=(16, 0))
    results.columnconfigure(1, weight=1)
    result_values = [tk.StringVar(master=root, value="—") for _ in result_labels]
    for row, (label, variable) in enumerate(zip(result_labels, result_values)):
        ttk.Label(results, text=label).grid(row=row, column=0, sticky="nw", padx=(0, 16), pady=6)
        wrapping_label(results, textvariable=variable, style="SimpleCalc.Value.TLabel").grid(
            row=row, column=1, sticky="ew", pady=6,
        )

    details_row = len(result_labels)
    update_visual = None
    if result_visual is not None:
        visual_frame = ttk.Frame(results)
        visual_frame.grid(row=details_row, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        update_visual = result_visual(visual_frame)
        update_visual(None)
        details_row += 1

    details_text = tk.StringVar(master=root)
    details = ttk.Frame(results)
    details.columnconfigure(0, weight=1)
    wrapping_label(details, textvariable=details_text).grid(row=0, column=0, sticky="ew")
    details.grid(row=details_row+1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
    details.grid_remove()

    def hide_details():
        details.grid_remove()
        details_button.configure(text="Show details ▾")

    def toggle_details():
        if details.winfo_manager():
            hide_details()
        else:
            details.grid()
            details_button.configure(text="Hide details ▴")

    details_button = ttk.Button(results, text="Show details ▾", command=toggle_details, state="disabled")
    details_button.grid(row=details_row, column=0, columnspan=2, sticky="w", pady=(12, 0))

    def clear_results():
        for variable in result_values:
            variable.set("—")
        if update_visual is not None:
            update_visual(None)
        details_text.set("")
        hide_details()
        details_button.state(["disabled"])

    def calculate(*_):
        try:
            try:
                value = float(entry.get())
            except ValueError:
                raise ValueError(f"{input_label}: enter a number.") from None
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{input_label}: enter a finite number greater than zero.")
            answers, explanation = evaluator(value)
        except (ValueError, OverflowError, ZeroDivisionError) as error:
            clear_results()
            error_text.set(str(error))
            error_label.grid()
            return
        error_text.set("")
        error_label.grid_remove()
        for variable, answer in zip(result_values, answers):
            variable.set(answer)
        if update_visual is not None:
            update_visual(answers)
        details_text.set(explanation)
        details_button.state(["!disabled"])

    def reset():
        entry.delete(0, tk.END)
        error_text.set("")
        error_label.grid_remove()
        clear_results()
        viewport.yview_moveto(0)
        entry.focus_set()

    ttk.Button(actions, text="Calculate", command=calculate).pack(side=tk.LEFT)
    ttk.Button(actions, text="Reset", command=reset).pack(side=tk.LEFT, padx=(8, 0))
    entry.bind("<Return>", calculate)

    def scroll_page(event):
        if viewport.yview() != (0.0, 1.0):
            up = getattr(event, "delta", 0) > 0 or getattr(event, "num", None) == 4
            viewport.yview_scroll(-3 if up else 3, "units")
            return "break"

    def bind_scrolling(widget):
        for event_name in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            widget.bind(event_name, scroll_page, add="+")
        for child in widget.winfo_children():
            bind_scrolling(child)

    bind_scrolling(viewport)
    entry.focus_set()


def parallaxe_distance_UI2(root):
    def evaluate(parallax_arcsec):
        # Preserve the existing small-angle calculation and distance constants.
        distance_m = AU / ((pi / 180) * (parallax_arcsec / 3600))
        distance_pc, distance_ly = distance_m / psc, distance_m / ly
        if not all(math.isfinite(v) and v > 0 for v in (distance_m, distance_pc, distance_ly)):
            raise ValueError("Parallax is outside the supported numeric range.")
        answers = (f"{distance_pc:.6g} pc", f"{distance_ly:.6g} ly")
        details = (
            f"Parallax: {parallax_arcsec:.6g} arcseconds\n"
            f"Distance: {distance_m:.6e} m\n"
            f"Distance: {distance_pc / 1000:.6g} kpc\n"
            f"Distance: {distance_pc / 1e6:.6g} Mpc\n\n"
            "Model: distance = 1 AU / parallax angle in radians (small-angle approximation).\n"
            "Equivalent relation: distance in parsecs ≈ 1 / parallax in arcseconds.\n"
            "This estimate does not account for measurement uncertainty."
        )
        return answers, details

    _single_input_calculator_UI(
        root, "Estimate a star's distance from its annual parallax.",
        "Parallax", "arcsec", ("Distance", "In light-years"), evaluate,
        "Example: 0.1 arcsec. Enter a positive parallax angle.",
    )





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
    def evaluate(wavelength):
        energy_j, energy_ev = photon_energy(wavelength)
        frequency = c / wavelength
        if not all(math.isfinite(v) and v > 0 for v in (energy_j, energy_ev, frequency)):
            raise ValueError("Wavelength is outside the supported numeric range.")
        answers = (
            f"{energy_ev:.6g} eV",
            f"{energy_j:.6e} J",
            spectrum_name(wavelength),
        )
        details = (
            f"Wavelength: {wavelength:.6g} m\n"
            f"Frequency: {frequency:.6e} Hz\n\n"
            f"Energy: {energy_ev / 1e-9:.6g} neV\n"
            f"Energy: {energy_ev / 1e3:.6g} keV\n"
            f"Energy: {energy_ev / 1e6:.6g} MeV\n"
            f"Energy: {energy_ev / 1e9:.6g} GeV\n"
            f"Energy: {energy_ev / 1e12:.6g} TeV\n\n"
            "Model: frequency = c / wavelength; energy per photon = h × frequency.\n"
            "Wavelength and frequency are related using the speed of light in vacuum."
        )
        return answers, details

    _single_input_calculator_UI(
        root, "Calculate the energy of a photon from its wavelength.",
        "Wavelength", "m", ("Photon energy", "In joules", "Spectrum"), evaluate,
        "Example: 5e-7 m = 500 nm. Scientific notation is supported.",
    )


MS_colors = ['blue', 'blue', 'cyan', 'green', 'yellow', 'orange', 'red']
MS_absmag = [5.5, 5.0, 4.0, 3.0, 2.0, 1.5, 0.0]
MS_sptype = ['O', 'B', 'A', 'F', 'G', 'K', 'M']





def spectral_class3_UI(root):
    """Temperature-based stellar estimate with a highlighted spectral-class strip."""
    # Preserve the calculator's existing O–M thresholds and colour labels.
    classes = (
        ("O", 30000, "Blue", "#9bbcff", "T ≥ 30,000 K"),
        ("B", 10000, "Blue-White", "#c4d9ff", "10,000 ≤ T < 30,000 K"),
        ("A", 7500, "White", "#edf2ff", "7,500 ≤ T < 10,000 K"),
        ("F", 6000, "Yellow-White", "#fff8dc", "6,000 ≤ T < 7,500 K"),
        ("G", 5200, "Yellow", "#ffe58a", "5,200 ≤ T < 6,000 K"),
        ("K", 3700, "Orange", "#ffb570", "3,700 ≤ T < 5,200 K"),
        ("M", 0, "Red", "#ef8c82", "0 < T < 3,700 K"),
    )

    def evaluate(temperature):
        spectral_class, _, colour, _, temperature_range = next(
            row for row in classes if temperature >= row[1]
        )
        wavelength_nm = 2.898e6 / temperature
        if not math.isfinite(wavelength_nm) or wavelength_nm <= 0:
            raise ValueError("Temperature is outside the supported numeric range.")

        # Keep the existing peak-region classification for this UI update.
        if wavelength_nm < 0.01:
            region = "Gamma rays"
        elif wavelength_nm < 10:
            region = "X-rays"
        elif wavelength_nm < 400:
            region = "Ultraviolet"
        elif wavelength_nm < 700:
            region = "Visible light"
        elif wavelength_nm < 3000:
            region = "Infrared"
        elif wavelength_nm < 1000000:
            region = "Microwaves"
        else:
            region = "Radio waves"

        answers = (spectral_class, f"{wavelength_nm:.6g} nm", region)
        details = (
            f"Surface temperature: {temperature:,.6g} K\n"
            f"Estimated class: {spectral_class}\n"
            f"Temperature range in this model: {temperature_range}\n"
            f"Approximate colour label: {colour}\n\n"
            "Wien's displacement law (wavelength form):\n"
            "λ_peak = 2.898 × 10⁶ nm·K / T\n"
            f"λ_peak = 2.898 × 10⁶ / {temperature:.6g} = {wavelength_nm:.6g} nm\n\n"
            "The peak uses a blackbody approximation.\n"
            "The O–B–A–F–G–K–M classes here are temperature estimates; "
            "spectral features are needed for a full classification.\n"
            "The strip shows approximate class colours, not the colour of the peak wavelength."
        )
        return answers, details

    def build_class_strip(parent):
        parent.columnconfigure(0, weight=1)
        strip = ttk.Frame(parent)
        strip.grid(row=0, column=0, sticky="ew")
        tiles = {}
        markers = {}
        for column, (name, _, _, colour, _) in enumerate(classes):
            strip.columnconfigure(column, weight=1, uniform="stellar_classes")
            tile = tk.Label(
                strip, text=name, width=2, padx=4, pady=10,
                background=colour, foreground="#172b40",
                font=("TkDefaultFont", 14, "bold"),
                relief="flat", borderwidth=0, highlightthickness=3,
                highlightbackground="#b8bdc4",
            )
            tile.grid(row=0, column=column, sticky="ew", padx=2)
            marker = ttk.Label(strip, text=" ", anchor="center")
            marker.grid(row=1, column=column, sticky="ew")
            tiles[name], markers[name] = tile, marker

        captions = ttk.Frame(parent)
        captions.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        ttk.Label(captions, text="← Hotter").pack(side=tk.LEFT)
        ttk.Label(captions, text="Cooler →").pack(side=tk.RIGHT)

        def update(answers):
            selected = answers[0] if answers is not None else None
            for name, tile in tiles.items():
                tile.configure(highlightbackground="#172b40" if name == selected else "#b8bdc4")
                markers[name].configure(text="▲" if name == selected else " ")

        return update

    _single_input_calculator_UI(
        root, "Estimate a star's spectral class and peak wavelength from its surface temperature.",
        "Surface temperature", "K",
        ("Estimated class", "Peak wavelength", "Peak spectrum region"), evaluate,
        "Example: 5800 K. Enter a positive surface temperature.",
        result_visual=build_class_strip,
    )





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
    """Build the Roche Limit tool inside its calculator tab."""
    for widget in root.winfo_children():
        widget.destroy()

    style = ttk.Style(root)
    style.configure("Roche.Value.TLabel", font=("TkDefaultFont", 16, "bold"))
    style.configure("Roche.Error.TLabel", foreground="#a12622")

    shell = ttk.Frame(root)
    shell.pack(fill=tk.BOTH, expand=True)
    shell.columnconfigure(0, weight=1)
    shell.rowconfigure(0, weight=1)
    viewport = tk.Canvas(
        shell, width=1, height=1, highlightthickness=0,
        background=style.lookup("TFrame", "background") or "#eeeeee",
    )
    viewport.grid(row=0, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(shell, orient="vertical", command=viewport.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    viewport.configure(yscrollcommand=scrollbar.set)

    page = ttk.Frame(viewport, padding=(4, 4, 16, 16))
    page.columnconfigure(0, weight=1)
    page_item = viewport.create_window(0, 0, window=page, anchor="nw")

    def update_scroll_region(_event=None):
        viewport.configure(scrollregion=viewport.bbox("all"))

    def resize_page(event):
        viewport.itemconfigure(page_item, width=max(1, event.width))

    viewport.bind("<Configure>", resize_page)
    page.bind("<Configure>", update_scroll_region)

    def wrapping_label(parent, **kwargs):
        label = ttk.Label(parent, width=1, wraplength=1, justify=tk.LEFT, **kwargs)

        def resize_text(event):
            width = max(1, event.width - 4)
            if int(label.cget("wraplength")) != width:
                label.configure(wraplength=width)

        label.bind("<Configure>", resize_text)
        return label

    wrapping_label(
        page, text="Estimate the distance at which tidal forces can disrupt a secondary body.",
    ).grid(row=0, column=0, sticky="ew", pady=(0, 16))

    inputs = ttk.LabelFrame(page, text="Inputs", padding=16)
    inputs.grid(row=1, column=0, sticky="ew")
    inputs.columnconfigure(1, weight=1)

    def make_input(row, label, unit):
        ttk.Label(inputs, text=label).grid(
            row=row, column=0, sticky="w", padx=(0, 16), pady=6,
        )
        entry = ttk.Entry(inputs, width=14)
        entry.grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Label(inputs, text=unit).grid(
            row=row, column=2, sticky="w", padx=(8, 0), pady=6,
        )
        return entry

    radius_entry = make_input(0, "Primary radius", "km")
    rho_primary_entry = make_input(1, "Primary density", "g/cm³")
    rho_secondary_entry = make_input(2, "Secondary density", "g/cm³")

    actions = ttk.Frame(inputs)
    actions.grid(row=3, column=0, columnspan=3, sticky="w", pady=(12, 0))
    error_text = tk.StringVar(master=root)
    error_label = wrapping_label(
        inputs, textvariable=error_text, style="Roche.Error.TLabel",
    )
    error_label.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(8, 0))
    error_label.grid_remove()

    results = ttk.LabelFrame(page, text="Results", padding=16)
    results.grid(row=2, column=0, sticky="ew", pady=(16, 0))
    results.columnconfigure(1, weight=1)
    fluid_text = tk.StringVar(master=root, value="—")
    rigid_text = tk.StringVar(master=root, value="—")
    for row, (label, variable) in enumerate((
        ("Fluid limit", fluid_text), ("Rigid limit", rigid_text),
    )):
        ttk.Label(results, text=label).grid(
            row=row, column=0, sticky="w", padx=(0, 16), pady=6,
        )
        wrapping_label(
            results, textvariable=variable, style="Roche.Value.TLabel",
        ).grid(row=row, column=1, sticky="ew", pady=6)

    wrapping_label(
        results, text="Distances are measured from the primary body's centre.",
    ).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    details_text = tk.StringVar(master=root)
    details = ttk.Frame(results)
    details.columnconfigure(0, weight=1)
    details.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
    wrapping_label(details, textvariable=details_text).grid(
        row=0, column=0, sticky="ew",
    )
    details.grid_remove()

    def hide_details():
        details.grid_remove()
        details_button.configure(text="Show details ▾")

    def toggle_details():
        if details.winfo_manager():
            hide_details()
        else:
            details.grid()
            details_button.configure(text="Hide details ▴")

    details_button = ttk.Button(
        results, text="Show details ▾", command=toggle_details, state="disabled",
    )
    details_button.grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))

    def clear_results():
        fluid_text.set("—")
        rigid_text.set("—")
        details_text.set("")
        hide_details()
        details_button.state(["disabled"])

    def calculate(*_):
        try:
            values = []
            for entry, name in (
                (radius_entry, "Primary radius"),
                (rho_primary_entry, "Primary density"),
                (rho_secondary_entry, "Secondary density"),
            ):
                try:
                    value = float(entry.get())
                except ValueError:
                    raise ValueError(f"{name}: enter a number.") from None
                if not math.isfinite(value) or value <= 0:
                    raise ValueError(f"{name}: enter a finite number greater than zero.")
                values.append(value)

            radius_km, primary_g_cm3, secondary_g_cm3 = values
            radius_m = radius_km * 1000
            density_primary = primary_g_cm3 * 1000  # g/cm³ → kg/m³
            density_secondary = secondary_g_cm3 * 1000
            ratio = (density_primary / density_secondary) ** (1 / 3)
            fluid_m = 2.44 * radius_m * ratio
            rigid_m = 1.26 * radius_m * ratio
            if not all(math.isfinite(value) and value > 0 for value in (fluid_m, rigid_m)):
                raise ValueError("Values are outside the supported numeric range.")
        except (ValueError, OverflowError, ZeroDivisionError) as error:
            clear_results()
            error_text.set(str(error))
            error_label.grid()
            return

        error_text.set("")
        error_label.grid_remove()
        fluid_text.set(f"{fluid_m / 1000:,.3f} km")
        rigid_text.set(f"{rigid_m / 1000:,.3f} km")
        details_text.set(
            f"Primary radius: {radius_km:g} km\n"
            f"Primary density: {primary_g_cm3:g} g/cm³\n"
            f"Secondary density: {secondary_g_cm3:g} g/cm³\n\n"
            f"Fluid limit: {fluid_m / radiusearth:.3f} Earth radii\n"
            f"Rigid limit: {rigid_m / radiusearth:.3f} Earth radii\n\n"
            "Model: d = k × R × (primary density / secondary density)^(1/3).\n"
            "k = 2.44 for the fluid estimate; k = 1.26 for the rigid estimate.\n"
            "Idealised tidal estimates; material strength and other effects are omitted."
        )
        details_button.state(["!disabled"])

    def reset():
        for entry in (radius_entry, rho_primary_entry, rho_secondary_entry):
            entry.delete(0, tk.END)
        error_text.set("")
        error_label.grid_remove()
        clear_results()
        viewport.yview_moveto(0)
        radius_entry.focus_set()

    ttk.Button(actions, text="Calculate", command=calculate).pack(side=tk.LEFT)
    ttk.Button(actions, text="Reset", command=reset).pack(side=tk.LEFT, padx=(8, 0))
    for entry in (radius_entry, rho_primary_entry, rho_secondary_entry):
        entry.bind("<Return>", calculate)

    def scroll_page(event):
        if viewport.yview() != (0.0, 1.0):
            direction = -1 if event.delta > 0 or getattr(event, "num", None) == 4 else 1
            viewport.yview_scroll(direction * 3, "units")
            return "break"

    def bind_scrolling(widget):
        # Local bindings are removed with the tab; other calculators are unaffected.
        widget.bind("<MouseWheel>", scroll_page, add="+")
        widget.bind("<Button-4>", scroll_page, add="+")
        widget.bind("<Button-5>", scroll_page, add="+")
        for child in widget.winfo_children():
            bind_scrolling(child)

    bind_scrolling(viewport)
    radius_entry.focus_set()
