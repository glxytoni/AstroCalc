"""Shared 2D flyby mathematics and the integrated AstroCalc UI.

The standalone gravity_assist_concept.py also imports these mathematics.
Units: km, seconds, km/s, degrees. +x is the planet's orbital velocity;
positive angles are counter-clockwise. The incoming angle describes VELOCITY,
not the direction from the planet to the approaching spacecraft.

References:
https://orbital-mechanics.space/interplanetary-maneuvers/planetary-arrival-flyby.html
https://orbital-mechanics.space/the-orbit-equation/hyperbolic-trajectories.html
https://ssd.jpl.nasa.gov/planets/approx_pos.html
Planet masses/radii match AstroCalc's approximate constants. Orbital radii
are rounded semimajor axes; circular orbits are assumed, not ephemerides.
"""

import math
import tkinter as tk
from tkinter import ttk

G_KM = 6.6741e-20
SUN_MU = G_KM * 1.98847e30
AU_KM = 149597870.7
# Mass kg, radius km, approximate orbital radius AU, drawing colour.
PLANETS = {
    'Mercury': (3.3011e23, 2439.7, 0.3871, '#a3a3a3'),
    'Venus': (4.8675e24, 6051.8, 0.7233, '#e6c87a'),
    'Earth': (5.9722e24, 6371.0, 1.0000, '#397cff'),
    'Mars': (6.4171e23, 3389.5, 1.5237, '#c1440e'),
    'Jupiter': (1.8982e27, 69911.0, 5.2029, '#d9b38c'),
    'Saturn': (5.6834e26, 58232.0, 9.5367, '#e8d8a8'),
    'Uranus': (8.6810e25, 25362.0, 19.1892, '#8de0e8'),
    'Neptune': (1.02413e26, 24622.0, 30.0699, '#4169e1'),
}


def rotate(vector, angle):
    x, y = vector
    c, s = math.cos(angle), math.sin(angle)
    return x*c-y*s, x*s+y*c


def heading(vector):
    """A zero velocity has no defined direction."""
    return None if math.hypot(*vector) < 1e-12 else math.degrees(math.atan2(vector[1], vector[0]))


def calculate_flyby(mu, radius_km, vinf_kms, incoming_deg, altitude_km,
                    turn_sign=1, planet_speed_kms=0.0):
    """Unpowered two-body hyperbola, plus patched Sun-frame velocity vectors.

    e = 1 + rp*v_inf²/mu; delta = 2*asin(1/e).
    turn_sign=+1 rotates velocity counter-clockwise; -1 clockwise.
    Sun-frame outputs are local encounter approximations, not solar infinity.
    """
    values = (mu, radius_km, vinf_kms, incoming_deg, altitude_km, planet_speed_kms)
    if not all(math.isfinite(v) for v in values):
        raise ValueError('All inputs must be finite numbers.')
    if mu <= 0 or radius_km <= 0 or vinf_kms <= 0:
        raise ValueError('Gravity, radius and incoming v∞ must be positive.')
    if altitude_km <= 0:
        raise ValueError('Closest-approach altitude must be above the surface (greater than 0 km).')
    if planet_speed_kms < 0 or turn_sign not in (-1, 1):
        raise ValueError('Invalid planet speed or turn direction.')
    rp = radius_km + altitude_km
    e = 1 + rp*vinf_kms**2/mu
    if not math.isfinite(e) or e <= 1:
        raise ValueError('These values are outside the supported hyperbolic range.')
    delta = 2*math.asin(1/e)
    nu_inf = math.acos(-1/e)
    alpha = math.radians(incoming_deg % 360)
    # Orient the periapsis so the inbound asymptotic VELOCITY is at alpha.
    omega = alpha - turn_sign*(math.pi-nu_inf)
    vin = (vinf_kms*math.cos(alpha), vinf_kms*math.sin(alpha))
    vout = rotate(vin, turn_sign*delta)
    sun_in = (vin[0]+planet_speed_kms, vin[1])
    sun_out = (vout[0]+planet_speed_kms, vout[1])
    p = rp*(1+e)
    periapsis_speed = math.sqrt(vinf_kms**2+2*mu/rp)
    impact_parameter = rp*math.sqrt(1+2*mu/(rp*vinf_kms**2))
    if not all(math.isfinite(v) for v in (p, periapsis_speed, impact_parameter)):
        raise ValueError('These values exceed the supported numerical range.')
    return dict(mu=mu, radius_km=radius_km, rp=rp, e=e, p=p, delta=delta,
                nu_inf=nu_inf, omega=omega, turn_sign=turn_sign, vinf=vinf_kms,
                vin=vin, vout=vout, sun_in=sun_in, sun_out=sun_out,
                planet_speed=planet_speed_kms, periapsis_speed=periapsis_speed,
                impact_parameter=impact_parameter)


def flyby_state(flyby, nu):
    """Position and velocity at true anomaly nu, in the drawing's planet frame."""
    e, p, sign = flyby['e'], flyby['p'], flyby['turn_sign']
    denominator = 1+e*math.cos(nu)
    if denominator <= 0 or abs(nu) >= flyby['nu_inf']:
        raise ValueError('True anomaly must lie inside the hyperbolic asymptotes.')
    r = p/denominator
    factor = math.sqrt(flyby['mu']/p)
    position = rotate((r*math.cos(nu), sign*r*math.sin(nu)), flyby['omega'])
    velocity = rotate((-factor*math.sin(nu), sign*factor*(e+math.cos(nu))), flyby['omega'])
    return position, velocity


def flyby_points(flyby, extent=6.0, steps=400):
    """Sample a finite plot, not an SOI boundary or a point at infinity."""
    if extent <= 1 or steps < 2:
        raise ValueError('Plot extent must exceed periapsis; at least two steps required.')
    limit = math.acos((flyby['p']/(extent*flyby['rp'])-1)/flyby['e'])
    return [flyby_state(flyby, -limit+2*limit*i/steps)[0] for i in range(steps+1)]



def gravity_assist_UI(root):
    """Scrollable UI 2.0 encounter tool with a zoomable planet-centred diagram."""
    for widget in root.winfo_children():
        widget.destroy()
    style = ttk.Style(root)
    style.configure('Flyby.Value.TLabel', font=('TkDefaultFont', 16, 'bold'))
    style.configure('Flyby.Error.TLabel', foreground='#a12622')
    shell = ttk.Frame(root)
    shell.pack(fill=tk.BOTH, expand=True)
    shell.columnconfigure(0, weight=1)
    shell.rowconfigure(0, weight=1)
    viewport = tk.Canvas(shell, width=1, height=1, highlightthickness=0,
                         background=style.lookup('TFrame', 'background') or '#eeeeee')
    viewport.grid(row=0, column=0, sticky='nsew')
    scrollbar = ttk.Scrollbar(shell, orient='vertical', command=viewport.yview)
    scrollbar.grid(row=0, column=1, sticky='ns')
    viewport.configure(yscrollcommand=scrollbar.set)
    page = ttk.Frame(viewport, padding=(4, 4, 16, 16))
    page.columnconfigure(0, weight=1)
    page_item = viewport.create_window(0, 0, window=page, anchor='nw')
    page.bind('<Configure>', lambda event: viewport.configure(scrollregion=viewport.bbox('all')))

    def wrap_label(parent, **options):
        label = ttk.Label(parent, width=1, wraplength=1, justify=tk.LEFT, **options)
        def fit(event):
            width = max(1, event.width-4)
            if int(label.cget('wraplength')) != width:
                label.configure(wraplength=width)
        label.bind('<Configure>', fit)
        return label

    wrap_label(page, text='Explore a 2D, unpowered planetary flyby. Positive angles are counter-clockwise from the planet’s motion.').grid(
        row=0, column=0, sticky='ew', pady=(0, 12))
    body = ttk.Frame(page)
    body.grid(row=1, column=0, sticky='ew')
    setup = ttk.LabelFrame(body, text='Flyby setup', padding=16)
    setup.columnconfigure(0, weight=1)
    view = ttk.LabelFrame(body, text='Planet-centred flyby', padding=12)
    view.columnconfigure(0, weight=1)
    defaults = dict(planet='Earth', vinf='6', angle='90', altitude='1000', turn='Clockwise')
    variables = {key: tk.StringVar(master=root, value=value) for key, value in defaults.items()}
    widgets = {}
    fields = [('Planet', 'planet', tuple(PLANETS)),
              ('Incoming v∞ [km/s] — planet-relative', 'vinf', None),
              ('Incoming velocity angle [°]', 'angle', None),
              ('Closest-approach altitude [km]', 'altitude', None),
              ('Turn direction', 'turn', ('Clockwise', 'Counter-clockwise'))]
    for index, (label, key, choices) in enumerate(fields):
        wrap_label(setup, text=label).grid(row=2*index, column=0, sticky='ew', pady=(6, 3))
        widget = (ttk.Combobox(setup, textvariable=variables[key], values=choices,
                              state='readonly', width=12)
                  if choices else ttk.Entry(setup, textvariable=variables[key], width=12))
        widget.grid(row=2*index+1, column=0, sticky='ew', pady=(0, 6))
        widgets[key] = widget
    wrap_label(setup, text='0° = right, 90° = up. This is the incoming velocity direction, not the object’s position. Altitude is above the reference surface.').grid(
        row=10, column=0, sticky='ew', pady=(8, 0))
    actions = ttk.Frame(setup)
    actions.grid(row=11, column=0, sticky='ew', pady=(12, 0))
    actions.columnconfigure(0, weight=1)
    actions.columnconfigure(1, weight=1)
    error_text = tk.StringVar(master=root)
    error_label = wrap_label(setup, textvariable=error_text, style='Flyby.Error.TLabel')
    error_label.grid(row=12, column=0, sticky='ew', pady=(10, 0))
    error_label.grid_remove()

    canvas = tk.Canvas(view, width=1, height=400, background='#10151e',
                       highlightthickness=0, cursor='hand2')
    canvas.grid(row=0, column=0, sticky='ew')
    navigation = ttk.Frame(view)
    navigation.grid(row=1, column=0, sticky='ew', pady=(10, 0))
    zoom_text = tk.StringVar(master=root, value='100%')
    wrap_label(view, text='Wheel: zoom • Drag: pan\nBlue: incoming • Orange: outgoing • White: closest approach\nFinite local sketch—not the sphere-of-influence boundary.').grid(
        row=2, column=0, sticky='ew', pady=(10, 0))
    wrap_label(page, text='Ideal two-body flyby and circular planetary orbit. No atmosphere, ring-clearance assessment, burns or three-body effects. Very low passes may be physically unsafe.').grid(
        row=2, column=0, sticky='ew', pady=(12, 0))

    results = ttk.LabelFrame(page, text='Results', padding=16)
    results.grid(row=3, column=0, sticky='ew', pady=(16, 0))
    results.columnconfigure(0, weight=1)
    planet_text = tk.StringVar(master=root, value='—')
    sun_text = tk.StringVar(master=root, value='—')
    summary_text = tk.StringVar(master=root)
    wrap_label(results, text='Outgoing at infinity — planet frame').grid(row=0, column=0, sticky='ew')
    wrap_label(results, textvariable=planet_text, style='Flyby.Value.TLabel').grid(row=1, column=0, sticky='ew', pady=(6, 12))
    wrap_label(results, text='Sun-relative speed change — local encounter').grid(row=2, column=0, sticky='ew')
    wrap_label(results, textvariable=sun_text, style='Flyby.Value.TLabel').grid(row=3, column=0, sticky='ew', pady=(6, 12))
    wrap_label(results, textvariable=summary_text).grid(row=4, column=0, sticky='ew')
    details_text = tk.StringVar(master=root)
    detail_label = wrap_label(results, textvariable=details_text)
    detail_label.grid(row=6, column=0, sticky='ew', pady=(12, 0))
    detail_label.grid_remove()
    state = {'data': None, 'points': None, 'color': '#397cff', 'name': 'Earth', 'expanded': False}
    camera = {'zoom': 1.0, 'x': 0.0, 'y': 0.0, 'drag': None}

    def draw(_event=None):
        width, height = canvas.winfo_width(), canvas.winfo_height()
        wanted_height = max(320, min(540, width))
        if int(canvas.cget('height')) != wanted_height:
            canvas.configure(height=wanted_height)
        canvas.delete('all')
        data = state['data']
        if data is None:
            canvas.create_text(width/2, height/2, text='Calculate a flyby to draw its trajectory.',
                               fill='#e6edf5', width=max(1, width-30))
            return
        if min(width, height) < 120:
            return
        scale = (min(width, height)/2-42)/(6*data['rp'])*camera['zoom']
        cx, cy = width/2+camera['x'], height/2+camera['y']
        def screen(point):
            return cx+point[0]*scale, cy-point[1]*scale
        canvas.create_line(12, cy, width-12, cy, fill='#707d91', dash=(5, 5), arrow=tk.LAST)
        canvas.create_text(width-12, cy+12, anchor='ne', fill='#c9d1df',
                           text='Planet motion → 0°', font=('TkDefaultFont', 10))
        actual_radius = data['radius_km']*scale
        radius = max(3, actual_radius)
        canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius,
                           fill=state['color'], outline='', tags='planet')
        points = state['points']
        mid = len(points)//2
        for segment, colour, tag in ((points[:mid+1], '#68d7ff', 'incoming'),
                                     (points[mid:], '#ffbd66', 'outgoing')):
            flat = [v for point in segment for v in screen(point)]
            canvas.create_line(*flat, fill=colour, width=2, tags=tag)
            index = len(segment)//2
            canvas.create_line(*screen(segment[index-3]), *screen(segment[index+3]),
                               fill=colour, width=2, arrow=tk.LAST)
        px, py = screen(points[mid])
        canvas.create_line(cx, cy, px, py, fill='#b9c3d3', dash=(3, 4))
        canvas.create_oval(px-4, py-4, px+4, py+4, fill='white', outline='', tags='periapsis')
        canvas.create_text(px, py+10, text='Closest approach', anchor='n', fill='white',
                           font=('TkDefaultFont', 10))
        canvas.create_text(12, 12, anchor='nw', fill='#e6edf5', text=state['name'],
                           font=('TkDefaultFont', 12, 'bold'))
        # Fixed inset shows asymptotic directions separately from finite curve endpoints.
        ox, oy, length = 64, height-64, 34
        canvas.create_rectangle(6, height-110, 124, height-6, fill='#10151e', outline='#354253')
        canvas.create_line(ox-40, oy, ox+43, oy, fill='#707d91', arrow=tk.LAST)
        for velocity, colour in ((data['vin'], '#68d7ff'), (data['vout'], '#ffbd66')):
            vx, vy = velocity
            canvas.create_line(ox, oy, ox+length*vx/data['vinf'], oy-length*vy/data['vinf'],
                               fill=colour, width=2, arrow=tk.LAST)
        canvas.create_text(14, height-14, anchor='sw', text='v∞ directions', fill='#e6edf5',
                           font=('TkDefaultFont', 10))
        if actual_radius < 3:
            canvas.create_text(width-10, height-12, anchor='se', fill='#e6edf5',
                               text='Planet marker enlarged', font=('TkDefaultFont', 9))

    def fit_view():
        camera.update(zoom=1.0, x=0.0, y=0.0, drag=None)
        zoom_text.set('100%')
        draw()

    def zoom_at(factor, x=None, y=None):
        if state['data'] is None:
            return
        x = canvas.winfo_width()/2 if x is None else x
        y = canvas.winfo_height()/2 if y is None else y
        new_zoom = max(.1, min(100, camera['zoom']*factor))
        ratio = new_zoom/camera['zoom']
        camera['x'] = x-canvas.winfo_width()/2-(x-canvas.winfo_width()/2-camera['x'])*ratio
        camera['y'] = y-canvas.winfo_height()/2-(y-canvas.winfo_height()/2-camera['y'])*ratio
        camera['zoom'] = new_zoom
        zoom_text.set(f'{new_zoom:.0%}')
        draw()

    def wheel_zoom(event):
        up = getattr(event, 'delta', 0) > 0 or getattr(event, 'num', None) == 4
        zoom_at(1.25 if up else .8, event.x, event.y)
        return 'break'

    def begin_drag(event):
        camera['drag'] = (event.x, event.y)

    def drag(event):
        if camera['drag'] is not None and state['data'] is not None:
            x, y = camera['drag']
            camera['x'] += event.x-x
            camera['y'] += event.y-y
            camera['drag'] = (event.x, event.y)
            draw()

    for event_name in ('<MouseWheel>', '<Button-4>', '<Button-5>'):
        canvas.bind(event_name, wheel_zoom)
    canvas.bind('<ButtonPress-1>', begin_drag)
    canvas.bind('<B1-Motion>', drag)
    canvas.bind('<ButtonRelease-1>', lambda event: camera.update(drag=None))
    canvas.bind('<Configure>', draw)
    ttk.Button(navigation, text='−', width=3, command=lambda: zoom_at(.8)).pack(side=tk.LEFT)
    ttk.Button(navigation, text='+', width=3, command=lambda: zoom_at(1.25)).pack(side=tk.LEFT, padx=4)
    ttk.Button(navigation, text='Fit flyby', command=fit_view).pack(side=tk.LEFT)
    ttk.Label(navigation, textvariable=zoom_text).pack(side=tk.LEFT, padx=8)

    def toggle_details():
        state['expanded'] = not state['expanded']
        if state['expanded']:
            detail_label.grid()
        else:
            detail_label.grid_remove()
        details_button.configure(text='Hide details ▴' if state['expanded'] else 'Show details ▾')
    details_button = ttk.Button(results, text='Show details ▾', command=toggle_details, state='disabled')
    details_button.grid(row=5, column=0, sticky='w', pady=(12, 0))

    def invalidate(*_args):
        state.update(data=None, points=None, expanded=False)
        camera['drag'] = None
        planet_text.set('—')
        sun_text.set('—')
        summary_text.set('Inputs changed — calculate to update.')
        details_text.set('')
        error_text.set('')
        error_label.grid_remove()
        detail_label.grid_remove()
        details_button.configure(state='disabled', text='Show details ▾')
        draw()

    def angle_text(vector):
        value = heading(vector)
        return 'undefined (zero speed)' if value is None else f'{value:+.2f}°'

    def calculate(_event=None):
        invalidate()
        try:
            name = variables['planet'].get()
            mass, radius, orbit_au, colour = PLANETS[name]
            data = calculate_flyby(
                G_KM*mass, radius, float(variables['vinf'].get()), float(variables['angle'].get()),
                float(variables['altitude'].get()), 1 if variables['turn'].get() == 'Counter-clockwise' else -1,
                math.sqrt(SUN_MU/(orbit_au*AU_KM)))
            points = flyby_points(data)
        except (ValueError, ArithmeticError, KeyError) as exc:
            error_text.set(f'Check inputs: {exc}')
            error_label.grid()
            viewport.yview_moveto(0)
            return
        state.update(data=data, points=points, color=colour, name=name)
        before, after = math.hypot(*data['sun_in']), math.hypot(*data['sun_out'])
        planet_text.set(f"{math.hypot(*data['vout']):,.4f} km/s  •  {angle_text(data['vout'])}")
        sun_text.set(f"{after-before:+,.4f} km/s")
        summary_text.set(
            f"Sun-relative speed: {before:,.4f} → {after:,.4f} km/s\n"
            f"Outgoing Sun-relative direction: {angle_text(data['sun_out'])}\n"
            f"Turn angle: {data['turn_sign']*math.degrees(data['delta']):+.2f}°\n"
            'Planet-relative v∞ speed is unchanged; its direction changes.')
        details_text.set(
            f"Planet: {name}\nRadius: {radius:,.1f} km\n"
            f"Assumed circular orbital speed: {data['planet_speed']:.4f} km/s\n"
            f"Incoming v∞ direction: {angle_text(data['vin'])}\n"
            f"Closest-approach altitude: {data['rp']-radius:,.3f} km\n"
            f"Closest-approach radius (from centre): {data['rp']:,.3f} km\n"
            f"Closest-approach speed: {data['periapsis_speed']:.4f} km/s\n"
            f"Eccentricity: {data['e']:.6g}\nImpact parameter: {data['impact_parameter']:,.3f} km\n\n"
            'e = 1 + rp × v∞² / μ\nTurning magnitude δ = 2 × asin(1/e)\n'
            'Outgoing v∞ is the incoming vector rotated by ±δ.\n'
            'Sun-relative velocity = planet orbital velocity + planet-relative v∞.\n\n'
            'Angles run from −180° to +180°, measured counter-clockwise from planet motion. '
            'The input angle orients the encounter; it is not the hyperbolic true anomaly.\n\n'
            'v∞ means the asymptotic planet-relative velocity, not the speed at a finite SOI boundary. '
            'Sun-frame results are local patched-encounter estimates, not velocities at infinity from the Sun. '
            'The plotted segment extends to six periapsis radii. No trajectory to another planet is computed.')
        details_button.configure(state='normal')
        fit_view()

    def reset():
        for key, value in defaults.items():
            variables[key].set(value)
        calculate()
        viewport.yview_moveto(0)
        widgets['vinf'].focus_set()

    calculate_button = ttk.Button(actions, text='Calculate & Draw', command=calculate)
    reset_button = ttk.Button(actions, text='Reset', command=reset)

    def resize_page(event):
        viewport.itemconfigure(page_item, width=max(1, event.width))
        narrow = event.width < 780
        body.columnconfigure(0, weight=1 if narrow else 4, uniform='' if narrow else 'flyby')
        body.columnconfigure(1, weight=0 if narrow else 5, uniform='' if narrow else 'flyby')
        setup.grid(row=0, column=0, sticky='new', padx=0 if narrow else (0, 16))
        view.grid(row=1 if narrow else 0, column=0 if narrow else 1, sticky='new',
                  pady=(16, 0) if narrow else 0)
        stacked_buttons = event.width < 440
        calculate_button.grid(row=0, column=0, columnspan=2 if stacked_buttons else 1, sticky='ew')
        reset_button.grid(row=1 if stacked_buttons else 0, column=0 if stacked_buttons else 1,
                          columnspan=2 if stacked_buttons else 1, sticky='ew',
                          padx=0 if stacked_buttons else (8, 0), pady=(8, 0) if stacked_buttons else 0)
    viewport.bind('<Configure>', resize_page)

    def scroll_page(event):
        if viewport.yview() != (0.0, 1.0):
            up = getattr(event, 'delta', 0) > 0 or getattr(event, 'num', None) == 4
            viewport.yview_scroll(-3 if up else 3, 'units')
            return 'break'

    def bind_scrolling(widget):
        if widget is canvas:
            return
        for event_name in ('<MouseWheel>', '<Button-4>', '<Button-5>'):
            widget.bind(event_name, scroll_page)
        for child in widget.winfo_children():
            bind_scrolling(child)
    for variable in variables.values():
        variable.trace_add('write', invalidate)
    for widget in widgets.values():
        widget.bind('<Return>', calculate)
        widget.bind('<KP_Enter>', calculate)
    bind_scrolling(viewport)
    calculate()
