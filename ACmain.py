import aclib as mfc
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

tool_tabs = {}


def close_tool_tab(key):
    tab = tool_tabs.pop(key, None)
    if tab is None or not tab.winfo_exists():
        return

    selected_tab = notebook.select()
    if selected_tab == str(tab):
        tabs = notebook.tabs()
        index = notebook.index(tab)
        # Prefer the next calculator, then work left; Dashboard is the fallback.
        neighbours = tabs[index + 1:] + tabs[:index][::-1]
        selected_tab = next(
            (tab_id for tab_id in neighbours if tab_id != str(dashboard)),
            str(dashboard),
        )

    notebook.forget(tab)
    tab.destroy()
    notebook.select(selected_tab)


def open_tool_tab(key, title, builder):
    existing_tab = tool_tabs.get(key)
    if existing_tab is not None and existing_tab.winfo_exists():
        notebook.select(existing_tab)
        return

    tool_tabs.pop(key, None)
    tab = ttk.Frame(notebook)
    tab.columnconfigure(0, weight=1)
    tab.rowconfigure(2, weight=1)

    header = ttk.Frame(tab, padding=(24, 16, 24, 8))
    header.grid(row=0, column=0, sticky="ew")
    header.columnconfigure(0, weight=1)
    ttk.Label(header, text=title, style="ToolTitle.TLabel").grid(
        row=0, column=0, sticky="w"
    )
    ttk.Button(
        header,
        text="Close tab",
        command=lambda: close_tool_tab(key),
    ).grid(row=0, column=1, sticky="e")
    ttk.Separator(tab).grid(row=1, column=0, sticky="ew")

    content = ttk.Frame(tab, padding=(20, 12))
    content.grid(row=2, column=0, sticky="nsew")

    tool_tabs[key] = tab
    notebook.add(tab, text=title)
    notebook.select(tab)
    builder(content)


def open_rel_kin_energy():
    open_tool_tab("relativistic_energy", "Relativistic Kinetic Energy", mfc.relativistic_kinetic_energy_UI2)


def open_mass_energy():
    open_tool_tab("mass_energy", "Mass-Energy Calculator", mfc.relativistic_kinetic_energy_UI4)


def open_photon_energy_spectrum():
    open_tool_tab("photon_spectrum", "Photon Energy / Spectrum", mfc.photon_energy_spectrum_UI)


def open_parallaxe_distance():
    open_tool_tab("parallax_distance", "Parallax Distance", mfc.parallaxe_distance_UI2)


def open_schwarzschild_radius():
    open_tool_tab("schwarzschild_radius", "Schwarzschild Radius", mfc.schwarzschild_radius_UI2)


def open_spectral_class():
    open_tool_tab("stellar_spectrum", "Stellar Spectrum", mfc.spectral_class3_UI)


def open_hohmann_transfer():
    open_tool_tab("hohmann_transfer", "Hohmann Transfer", mfc.hohmann_transfer_UI4)


def open_rocket_dV():
    open_tool_tab("rocket_delta_v", "Rocket DeltaV", mfc.rocket_deltaV_UI5)


def open_stellar_mag():
    open_tool_tab("stellar_magnitude", "Stellar Magnitude", mfc.stellar_magnitude_UI2)


def open_roche_limit():
    open_tool_tab("roche_limit", "Roche Limit", mfc.roche_limit_UI)


def open_orbit_visualizer():
    open_tool_tab("orbit_visualizer", "Orbit Visualizer", mfc.orbit_visualizer_UI3)


def open_redshift_distance():
    open_tool_tab("redshift_distance", "Redshift Distance", mfc.redshift_distance_UI)


root = tk.Tk()
root.title("AstroCalc 0.3.4")
root.geometry("900x700")
root.minsize(760, 580)

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
style.configure("ToolTitle.TLabel", font=("TkDefaultFont", 18, "bold"))


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
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky="nsew")

dashboard = ttk.Frame(notebook, padding=32)
notebook.add(dashboard, text="Dashboard")
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
