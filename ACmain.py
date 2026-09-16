import aclib as mfc
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk


def open_rel_kin_energy():
    rel_kin_energy_window = tk.Toplevel(root)
    mfc.relativistic_kinetic_energy_UI2(rel_kin_energy_window)


def open_mass_energy():
    mass_energy_window = tk.Toplevel(root)
    mfc.relativistic_kinetic_energy_UI4(mass_energy_window)


def open_photon_energy_spectrum():
    photon_energy_spectrum_window = tk.Toplevel(root)
    mfc.photon_energy_spectrum_UI(photon_energy_spectrum_window)


def open_parallaxe_distance():
    parallaxe_distance_window = tk.Toplevel(root)
    mfc.parallaxe_distance_UI2(parallaxe_distance_window)


def open_schwarzschild_radius():
    schwarzschild_radius_window = tk.Toplevel(root)
    mfc.schwarzschild_radius_UI2(schwarzschild_radius_window)


def open_spectral_class():
    spectral_class_window = tk.Toplevel(root)
    mfc.spectral_class3_UI(spectral_class_window)


def open_hohmann_transfer():
    hohman_transfer_window = tk.Toplevel(root)
    mfc.hohmann_transfer_UI4(hohman_transfer_window)


def open_rocket_dV():
    rocket_dV_window = tk.Toplevel(root)
    mfc.rocket_deltaV_UI5(rocket_dV_window)


def open_stellar_mag():
    stellar_mag_window = tk.Toplevel(root)
    mfc.stellar_magnitude_UI2(stellar_mag_window)


def open_roche_limit():
    roche_limit_window = tk.Toplevel(root)
    mfc.roche_limit_UI(roche_limit_window)


def open_orbit_visualizer():
    orbit_visualizer_window = tk.Toplevel(root)
    mfc.orbit_visualizer_UI3(orbit_visualizer_window)


def open_redshift_distance():
    redshift_distance_window = tk.Toplevel(root)
    mfc.redshift_distance_UI(redshift_distance_window)


root = tk.Tk()
root.title("AstroCalc 0.3.4")
root.geometry("760x480")
root.minsize(650, 420)

# Scale the shared Tk named fonts so existing calculator windows remain readable.
tkfont.nametofont("TkDefaultFont").configure(size=14)
tkfont.nametofont("TkTextFont").configure(size=14)
tkfont.nametofont("TkMenuFont").configure(size=13)

style = ttk.Style(root)
if "clam" in style.theme_names():
    style.theme_use("clam")
style.configure("Title.TLabel", font=("TkDefaultFont", 26, "bold"))
style.configure("Subtitle.TLabel", font=("TkDefaultFont", 13))
style.configure("Category.TMenubutton", font=("TkDefaultFont", 15, "bold"), padding=(20, 16))
style.configure("Footer.TLabel", font=("TkDefaultFont", 11))


# Create the menu
menu = tk.Menu(root)
root.config(menu=menu)


# Create Tools menu
tools_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Tools", menu=tools_menu)


# Physics & Relativity
physics_menu = tk.Menu(tools_menu, tearoff=0)
tools_menu.add_cascade(
    label="Physics & Relativity",
    menu=physics_menu
)

physics_menu.add_command(
    label="Relativistic Kinetic Energy",
    command=open_rel_kin_energy
)

physics_menu.add_command(
    label="Mass-Energy Calculator",
    command=open_mass_energy
)

physics_menu.add_command(
    label="Photon Energy / Spectrum",
    command=open_photon_energy_spectrum
)

physics_menu.add_command(
    label="Schwarzschild Radius",
    command=open_schwarzschild_radius
)

physics_menu.add_command(
    label="Relativistic Speed Kinetic Energy [WIP]"
)


# Orbital Mechanics
orbit_menu = tk.Menu(tools_menu, tearoff=0)
tools_menu.add_cascade(
    label="Orbital Mechanics",
    menu=orbit_menu
)

orbit_menu.add_command(
    label="Hohmann Transfer",
    command=open_hohmann_transfer
)

orbit_menu.add_command(
    label="Orbit Visualizer [WIP]",
    command=open_orbit_visualizer
)

orbit_menu.add_command(
    label="Patched-Conics Gravity Assist Visualizer [WIP]"
)

orbit_menu.add_command(
    label="Orbit Analysis [WIP]"
)

orbit_menu.add_command(
    label="Roche Limit",
    command=open_roche_limit
)


# Stellar Astronomy
stellar_menu = tk.Menu(tools_menu, tearoff=0)
tools_menu.add_cascade(
    label="Stellar Astronomy",
    menu=stellar_menu
)

stellar_menu.add_command(
    label="Stellar Magnitude",
    command=open_stellar_mag
)

stellar_menu.add_command(
    label="Stellar Spectrum",
    command=open_spectral_class
)

stellar_menu.add_command(
    label="Parallax Distance",
    command=open_parallaxe_distance
)

stellar_menu.add_command(
    label="Stellar Distance Estimation [WIP]"
)

stellar_menu.add_command(
    label="Stellar Constant [WIP]"
)


# Cosmology
cosmology_menu = tk.Menu(tools_menu, tearoff=0)
tools_menu.add_cascade(
    label="Cosmology",
    menu=cosmology_menu
)

cosmology_menu.add_command(
    label="Hubble Expansion via Redshift",
    command=open_redshift_distance
)


# Spaceflight & Propulsion
spaceflight_menu = tk.Menu(tools_menu, tearoff=0)
tools_menu.add_cascade(
    label="Spaceflight & Propulsion",
    menu=spaceflight_menu
)

spaceflight_menu.add_command(
    label="Rocket DeltaV",
    command=open_rocket_dV
)


# Main dashboard. The menu bar remains available as secondary navigation.
dashboard = ttk.Frame(root, padding=32)
dashboard.grid(sticky="nsew")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
dashboard.columnconfigure(0, weight=1)
dashboard.columnconfigure(1, weight=1)

ttk.Label(dashboard, text="AstroCalc", style="Title.TLabel").grid(
    row=0, column=0, columnspan=2, sticky="w"
)
ttk.Label(
    dashboard,
    text="Astronomy, physics, orbital-mechanics, and propulsion calculators",
    style="Subtitle.TLabel",
).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 28))

categories = (
    (
        "Physics & Relativity",
        (
            ("Relativistic Kinetic Energy", open_rel_kin_energy),
            ("Mass-Energy Calculator", open_mass_energy),
            ("Photon Energy / Spectrum", open_photon_energy_spectrum),
            ("Schwarzschild Radius", open_schwarzschild_radius),
            ("Relativistic Speed Kinetic Energy [Coming soon]", None),
        ),
    ),
    (
        "Orbits & Spaceflight",
        (
            ("Hohmann Transfer", open_hohmann_transfer),
            ("Orbit Visualizer", open_orbit_visualizer),
            ("Roche Limit", open_roche_limit),
            ("Rocket DeltaV", open_rocket_dV),
            ("Patched-Conics Gravity Assist [Coming soon]", None),
            ("Orbit Analysis [Coming soon]", None),
        ),
    ),
    (
        "Stellar Astronomy",
        (
            ("Stellar Magnitude", open_stellar_mag),
            ("Stellar Spectrum", open_spectral_class),
            ("Parallax Distance", open_parallaxe_distance),
            ("Stellar Distance Estimation [Coming soon]", None),
            ("Stellar Constant [Coming soon]", None),
        ),
    ),
    (
        "Cosmology",
        (("Hubble Expansion via Redshift", open_redshift_distance),),
    ),
)

for index, (category_name, tools) in enumerate(categories):
    row, column = divmod(index, 2)
    category_button = ttk.Menubutton(
        dashboard,
        text=f"{category_name}  ▾",
        style="Category.TMenubutton",
    )
    category_menu = tk.Menu(category_button, tearoff=False)
    for label, command in tools:
        category_menu.add_command(
            label=label,
            command=command,
            state=tk.NORMAL if command else tk.DISABLED,
        )
    category_button.configure(menu=category_menu)
    category_button.grid(
        row=row + 2,
        column=column,
        sticky="ew",
        padx=8,
        pady=8,
    )

ttk.Separator(dashboard).grid(
    row=4, column=0, columnspan=2, sticky="ew", pady=(28, 10)
)
ttk.Label(
    dashboard,
    text="Choose a category to open a calculator. Units are SI by default.",
    style="Footer.TLabel",
).grid(row=5, column=0, columnspan=2, sticky="w")


root.mainloop()
