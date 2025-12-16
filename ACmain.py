
import aclib as mfc
import tkinter as tk
from tkinter import ttk

# (Your constants and other code remain unchanged)

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
    mfc.hohmann_transfer_UI2(hohman_transfer_window)

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
    mfc.orbit_visualizer_UI(orbit_visualizer_window)



root = tk.Tk()
root.title("Astrocalc0.3.2")
root.option_add("*Font", "TkDefaultFont 20")  # Set default font for all widgets
root.option_add("*Label.Font", "TkDefaultFont 20")  # Set font for all labels
root.option_add("*MenuButton.Font", "TkDefaultFont 20")  # Set font for all menu buttons
root.geometry("500x350")

# create the menu
menu = tk.Menu(root)
root.config(menu=menu)

# create a dropdown menu for the tools
tools_menu = tk.Menu(menu)
menu.add_cascade(label="Tools", menu=tools_menu)

# add the available tools as menu options
tools_menu.add_command(label="- Photon Energy/Spectrum", command=open_photon_energy_spectrum)
tools_menu.add_command(label="- Parallaxe Distance", command=open_parallaxe_distance)
tools_menu.add_command(label="- Hohmann Transfer", command=open_hohmann_transfer)
tools_menu.add_command(label="- Schwarzchild Radius", command=open_schwarzschild_radius)
tools_menu.add_command(label="- Rocket DeltaV", command=open_rocket_dV)
tools_menu.add_command(label="- Stellar Magnitude", command=open_stellar_mag)
tools_menu.add_command(label="- Stellar Spectrum", command=open_spectral_class)
tools_menu.add_command(label="- Roche Limit", command=open_roche_limit)
tools_menu.add_command(label="- Orbit Visualizer", command=open_orbit_visualizer)

tools_menu.add_command(label="2D Orbit Plot [WIP]")
tools_menu.add_command(label="Orbit Analysis [WIP]")
tools_menu.add_command(label="Relativistic Speed Kinetic Energy [WIP]")
tools_menu.add_command(label="Hubble Expansion via Redshift [WIP]")
tools_menu.add_command(label="Stellar Distance Estimation [WIP]")
tools_menu.add_command(label="Stellar Constant [WIP]")


root.mainloop()


