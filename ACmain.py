import aclib as mfc
import tkinter as tk
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
    mfc.orbit_visualizer_UI2(orbit_visualizer_window)


def open_redshift_distance():
    redshift_distance_window = tk.Toplevel(root)
    mfc.redshift_distance_UI(redshift_distance_window)


root = tk.Tk()
root.title("Astrocalc0.3.3")

root.option_add("*Font", "TkDefaultFont 20")
root.option_add("*Label.Font", "TkDefaultFont 20")
root.option_add("*MenuButton.Font", "TkDefaultFont 20")

root.geometry("500x350")


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


root.mainloop()