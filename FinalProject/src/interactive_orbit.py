# -*- coding: utf-8 -*-
"""
interactive_orbit.py — 实时交互轨道演示 (O6 / Rule 25)
=====================================================
基于 matplotlib Slider 的交互式轨道参数探索工具。

功能：
  - 调节发射日期 t₀、近日距 r_p、近月距 r_m、借力方向
  - 实时更新日心转移椭圆轨道图
  - 动态显示 Δv 分解和节能比例
  - 支持 Tkinter 后端和 Web (matplotlib %matplotlib widget)

用法：
  python src/interactive_orbit.py

作者：Claude Code (deepseek-v4-pro) + 用户审校
日期：2026-06-18
"""

import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # Interactive backend
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
from matplotlib.patches import Ellipse

# Project modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from nbody import AU, G_SUN, V_EARTH, R_SUN
from patched_conic import solve_patched_conic, solve_moon_flyby, V2_EARTH, MOON_ORBITAL_SPEED
from trajectory_optimizer import earth_orbit_state, compute_physical_residual_dv


def compute_orbit(t0_day, r_p_au, r_m_km, side):
    """计算轨道参数"""
    geo = earth_orbit_state(t0_day)
    r1 = geo['r1_km']
    v_e = geo['v_e_kms']
    r_p = r_p_au * AU

    try:
        sol = solve_patched_conic(rp=r_p, r1=r1, v_e=v_e)
    except ValueError:
        return None

    # Moon flyby
    v_inf_moon = abs(sol.delta_v) + MOON_ORBITAL_SPEED
    flyby = solve_moon_flyby(r_m_km, v_inf_moon)
    moon_dv = flyby.get('delta_v_max', 0.0) if flyby.get('is_valid') else 0.0

    if side == "leading":
        dv_departure = max(abs(sol.delta_v) - moon_dv * 0.5, 0.0)
    else:
        dv_departure = abs(sol.delta_v) + moon_dv * 0.3

    # Physical residual (Rule 17)
    moon_state = {'r_moon_km': 384400.0, 'moon_efficiency': 0.5}
    residual = compute_physical_residual_dv(
        sol, moon_state, r_m_km, side, dv_departure, moon_dv,
    )
    dv_residual = residual['dv_residual_total_kms']
    v_inf_re = abs(sol.delta_v)
    dv_reentry = np.sqrt(V2_EARTH**2 + v_inf_re**2) - V2_EARTH

    return {
        'sol': sol, 'dv_departure': dv_departure,
        'dv_residual': dv_residual, 'dv_reentry': dv_reentry,
        'dv_total': dv_departure + dv_residual + dv_reentry,
        'moon_dv': moon_dv, 'r1': r1, 'v_e': v_e,
    }


def main():
    print("=" * 60)
    print("Interactive Orbit Explorer (O6 / Rule 25)")
    print("  Adjust sliders to explore launch parameters")
    print("  Close window to exit")
    print("=" * 60)

    # Initial values
    t0_init = 180
    rp_init = 0.3
    rm_init = 5000.0

    fig = plt.figure(figsize=(12, 8))
    fig.suptitle('Interactive Heliocentric Transfer Orbit Explorer', fontsize=13)

    # Main orbit plot
    ax_orbit = fig.add_axes([0.05, 0.35, 0.55, 0.60])
    ax_orbit.set_aspect('equal')
    ax_orbit.set_xlim(-1.5*AU, 1.5*AU)
    ax_orbit.set_ylim(-1.5*AU, 1.5*AU)
    ax_orbit.set_xlabel('X [km]')
    ax_orbit.set_ylabel('Y [km]')
    ax_orbit.grid(True, alpha=0.2)

    # Earth orbit circle
    theta = np.linspace(0, 2*np.pi, 500)
    earth_circle, = ax_orbit.plot(AU*np.cos(theta), AU*np.sin(theta),
                                   '--', color='gray', linewidth=0.8)

    # Sun
    ax_orbit.scatter([0], [0], s=150, color='orange', zorder=5)

    # Transfer ellipse placeholder
    ellipse_line, = ax_orbit.plot([], [], 'b-', linewidth=1.8)
    earth_marker, = ax_orbit.plot([], [], 'go', markersize=8)
    perihelion_marker, = ax_orbit.plot([], [], 'ro', markersize=6)

    # Info text
    info_text = ax_orbit.text(0.02, 0.98, '', transform=ax_orbit.transAxes,
                              fontsize=9, family='monospace',
                              verticalalignment='top')

    # Sliders
    ax_t0 = fig.add_axes([0.65, 0.78, 0.30, 0.03])
    slider_t0 = Slider(ax_t0, 't0 [day]', 0, 364, valinit=t0_init, valfmt='%d')

    ax_rp = fig.add_axes([0.65, 0.70, 0.30, 0.03])
    slider_rp = Slider(ax_rp, 'rp [AU]', 0.05, 0.95, valinit=rp_init)

    ax_rm = fig.add_axes([0.65, 0.62, 0.30, 0.03])
    slider_rm = Slider(ax_rm, 'rm [km]', 1838, 50000, valinit=rm_init)

    # Radio buttons for side
    ax_radio = fig.add_axes([0.65, 0.48, 0.12, 0.10])
    radio = RadioButtons(ax_radio, ('leading', 'trailing'), active=0)

    def update(val=None):
        t0 = int(slider_t0.val)
        rp = slider_rp.val
        rm = slider_rm.val
        side = radio.value_selected

        result = compute_orbit(t0, rp, rm, side)

        if result is None:
            info_text.set_text('INVALID PARAMETERS')
            return

        sol = result['sol']
        a = sol.a
        e = sol.e
        b = a * np.sqrt(1 - e**2)
        c = a * e
        center_x = -c

        # Update ellipse
        E_vals = np.linspace(0, 2*np.pi, 400)
        x_ell = center_x + a * np.cos(E_vals)
        y_ell = b * np.sin(E_vals)
        ellipse_line.set_data(x_ell, y_ell)

        # Earth position on its orbit at departure
        earth_angle = np.arctan2(0, result['r1'])
        earth_marker.set_data([result['r1']], [0])

        # Perihelion marker
        perihelion_x = a - c
        perihelion_marker.set_data([perihelion_x], [0])

        # Update info
        lines = [
            f"Date: day {t0}",
            f"r1={result['r1']/AU:.3f} AU, ve={result['v_e']:.1f} km/s",
            f"a={a/AU:.3f} AU, e={e:.4f}, T={sol.T_orbit_days:.0f}d",
            f"--- Δv [{side}] ---",
            f"Depart: {result['dv_departure']:.2f} km/s",
            f"Residual: {result['dv_residual']:.2f} km/s",
            f"Reentry: {result['dv_reentry']:.2f} km/s",
            f"TOTAL: {result['dv_total']:.2f} km/s",
            f"Moon contrib: {result['moon_dv']:.3f} km/s",
        ]
        info_text.set_text('\n'.join(lines))

        fig.canvas.draw_idle()

    slider_t0.on_changed(update)
    slider_rp.on_changed(update)
    slider_rm.on_changed(update)
    radio.on_clicked(update)

    # Initial draw
    update()

    print("Interactive window opened. Adjust sliders to explore.")
    print("Close the figure window to exit.")
    plt.show()
    print("Interactive session ended.")


if __name__ == "__main__":
    main()
