# -*- coding: utf-8 -*-
"""
plot_results.py — 工程交付物可视化 (阶段 5)
==========================================
生成所有静态图 + MP4 轨道动画。

功能：
  1. 轨道转移二维轨迹图
  2. 能量守恒对数曲线图
  3. 365天窗口 Δv(t₀) 曲线图
  4. 历表残差图
  5. 30-60 秒 MP4 轨道全景动画（含月球借力 zoom-in）

用法：
  python src/plot_results.py          # 生成所有静态图
  python src/plot_results.py --full   # 含完整扫描 + 动画渲染

作者：Claude Code (deepseek-v4-pro) + 用户审校
日期：2026-06-17
"""

import os
import json
import sys
import numpy as np
from pathlib import Path

# 配置 matplotlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import LogFormatterMathtext
import matplotlib.animation as animation

# 项目模块
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbody import (
    Body, nbody_integrate, G_SUN, G_EARTH, G_MOON,
    AU, R_SUN, R_EARTH, R_MOON, V_EARTH, YEAR_SECONDS,
    energy_nbody, total_angular_momentum,
)
from patched_conic import solve_patched_conic, apply_moon_flyby
from trajectory_optimizer import (
    outer_scan, energy_saving_analysis, sensitivity_analysis,
    compute_physical_residual_dv, moon_phase_state,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = REPO_ROOT / "figures"
OUTPUT_DIR = REPO_ROOT / "output"
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 140, "savefig.dpi": 200,
    "font.size": 10, "axes.labelsize": 11, "axes.titlesize": 12,
})


# ============================================================
# 图 1: 轨道转移二维轨迹图
# ============================================================
def plot_orbit_trajectory():
    """绘制日心椭圆转移轨道 + 月球借力示意"""
    print("Plotting orbit trajectory...")
    fig, ax = plt.subplots(figsize=(10, 9))

    # 地球圆形轨道
    theta = np.linspace(0, 2*np.pi, 500)
    ax.plot(AU*np.cos(theta), AU*np.sin(theta), '--', color='gray',
            linewidth=0.8, label='Earth orbit (1 AU)')

    # 转移椭圆: a=0.6AU, e=0.6667, rp=0.2AU
    rp = 0.2 * AU
    a = (AU + rp) / 2
    e = (AU - rp) / (AU + rp)
    b = a * np.sqrt(1 - e**2)
    c = a * e
    center_x = -c

    E_vals = np.linspace(0, 2*np.pi, 600)
    x_ell = center_x + a * np.cos(E_vals)
    y_ell = b * np.sin(E_vals)
    ax.plot(x_ell, y_ell, 'b-', linewidth=1.8, label='Transfer ellipse')

    # 太阳
    ax.scatter([0], [0], s=180, color='orange', edgecolors='darkorange',
               linewidth=1.5, zorder=5, label='Sun')
    ax.scatter([center_x], [0], s=10, color='gray', alpha=0.4)  # second focus

    # 近日点
    rp_x = a - c
    ax.scatter([rp_x], [0], s=60, color='red', zorder=4, label=f'Perihelion ({rp/AU:.2f} AU)')

    # 地球出发/返回位置（远日点, x=-(a+c)）
    ap_x = -(a + c)
    ax.scatter([ap_x], [0], s=40, color='green', zorder=4, label='Earth departure')

    # 飞行方向箭头（红色）
    E_arr = np.linspace(np.pi, 0, 30)
    x_arr = center_x + a * np.cos(E_arr)
    y_arr = b * np.sin(E_arr)
    for i in range(0, len(E_arr)-1, 5):
        ax.annotate('', xy=(x_arr[i+1], y_arr[i+1]),
                    xytext=(x_arr[i], y_arr[i]),
                    arrowprops=dict(arrowstyle='->', color='red',
                                    lw=1.5, alpha=0.7))

    ax.set_aspect('equal')
    ax.set_xlim(-1.8*AU, 1.3*AU)
    ax.set_ylim(-1.2*AU, 1.2*AU)
    ax.set_xlabel('X [km]')
    ax.set_ylabel('Y [km]')
    ax.set_title('Heliocentric Transfer Orbit (rp = 0.2 AU)')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.25, linestyle='--')

    path = FIG_DIR / "orbit_trajectory.png"
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


# ============================================================
# 图 2: 能量守恒对数曲线
# ============================================================
def plot_energy_conservation():
    """绘制四体系统 1 年能量与角动量守恒历史"""
    print("Plotting energy conservation...")
    from nbody import make_sun_earth_moon_rocket

    bodies = make_sun_earth_moon_rocket()
    result = nbody_integrate(bodies, h=3600.0, T=YEAR_SECONDS, check_interval=100)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    t_check = result.energy_check_steps * 3600.0 / 86400.0  # convert to days

    ax1.semilogy(t_check, result.energy_history + 1e-30, 'b-', linewidth=1.2)
    ax1.set_xlabel('Time [days]')
    ax1.set_ylabel('Relative Energy Drift |ΔE/E₀|')
    ax1.set_title('Energy Conservation')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(1e-6, color='red', linestyle='--', alpha=0.5, label='1e-6 threshold')
    ax1.legend(fontsize=8)

    ax2.semilogy(t_check, result.angular_momentum_history + 1e-30, 'r-', linewidth=1.2)
    ax2.set_xlabel('Time [days]')
    ax2.set_ylabel('Relative Angular Momentum Drift |ΔL/L₀|')
    ax2.set_title('Angular Momentum Conservation')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(1e-6, color='blue', linestyle='--', alpha=0.5, label='1e-6 threshold')
    ax2.legend(fontsize=8)

    fig.suptitle('Sun-Earth-Moon-Rocket: 1-Year Conservation')
    plt.tight_layout()

    path = FIG_DIR / "energy_conservation.png"
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


# ============================================================
# 图 3: 365 天窗口 Δv(t₀) 曲线
# ============================================================
def plot_dv_vs_launch_date():
    """
    绘制 Δv_total 随发射日期变化曲线 (M6)。

    使用地球轨道偏心率模型计算每天实际的 r1 和 v_e，
    通过 patched_conic + moon flyby 获得含月球借力的 Δv(t₀)。
    每 5 天采样以提升速度。
    """
    print("Plotting Δv vs launch date...")
    from trajectory_optimizer import (
        earth_orbit_state, solve_moon_flyby, MOON_ORBITAL_SPEED, V2_EARTH,
    )

    r_p = 0.3 * AU  # 典型近日距
    r_m = 5000.0    # 典型近月距
    dv_array = np.full(365, np.nan)

    for day in range(0, 365, 5):  # every 5 days
        try:
            geo = earth_orbit_state(day)
            r1 = geo['r1_km']
            v_e = geo['v_e_kms']
            sol = solve_patched_conic(rp=r_p, r1=r1, v_e=v_e)

            # 月球借力
            v_inf_moon = abs(sol.delta_v) + MOON_ORBITAL_SPEED
            flyby = solve_moon_flyby(r_m, v_inf_moon)
            moon_dv = flyby.get('delta_v_max', 0.0) if flyby.get('is_valid') else 0.0
            dv_earth = max(abs(sol.delta_v) - moon_dv * 0.5, 0.0)  # leading side
            ms = moon_phase_state(day)
            dv_res = compute_physical_residual_dv(
                sol, ms, r_m, "leading", dv_earth, moon_dv,
            )['dv_residual_total_kms']
            v_inf_re = abs(sol.delta_v)
            dv_reentry = np.sqrt(V2_EARTH**2 + v_inf_re**2) - V2_EARTH
            dv_array[day] = dv_earth + dv_res + dv_reentry
        except ValueError:
            pass

    # Interpolate missing days
    valid_mask = ~np.isnan(dv_array)
    if valid_mask.sum() > 1:
        from numpy import interp
        dv_array[~valid_mask] = np.interp(
            np.where(~valid_mask)[0],
            np.where(valid_mask)[0],
            dv_array[valid_mask],
        )

    fig, ax = plt.subplots(figsize=(11, 4.5))
    days = np.arange(365)
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    ax.plot(days, dv_array, 'b-', linewidth=1.2)
    ax.fill_between(days, np.nanmin(dv_array)*0.98, dv_array, alpha=0.15, color='blue')

    # 标记最优日期
    best_day = np.nanargmin(dv_array)
    ax.axvline(best_day, color='red', linestyle='--', alpha=0.6,
               label=f'Best: day {best_day} ({dv_array[best_day]:.3f} km/s)')

    ax.set_xlabel('Launch Date (2026)')
    ax.set_ylabel(r'$\Delta v_{\mathrm{total}}$ [km/s]')
    ax.set_title(r'$\Delta v_{\mathrm{total}}(t_0)$ — 2026 Launch Window Scan ($r_p$=0.3 AU, leading side)')
    ax.set_xticks(np.arange(15, 365, 30))
    ax.set_xticklabels(months, ha='center')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    path = FIG_DIR / "dv_vs_launch_date.png"
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


# ============================================================
# 图 4: 历表残差图
# ============================================================
def plot_residuals():
    """绘制 JPL 历表残差图"""
    print("Plotting residual history...")
    residuals_path = OUTPUT_DIR / "horizons_verify" / "residuals_2026.csv"
    if not residuals_path.exists():
        print(f"  [SKIP] No residual data at {residuals_path}")
        print(f"  Run: python src/horizons_verify.py first")
        return

    import pandas as pd
    df = pd.read_csv(residuals_path)

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))

    for name, color, ax_row in zip(
        ["Sun", "Earth", "Moon"],
        ["orange", "green", "gray"],
        [(0,0), (0,1), (1,0)]
    ):
        ax = axes[ax_row]
        ax.plot(df["day"], df[f"{name}_eps_r_km"], color=color, linewidth=1.2,
                label=f'{name} pos err')
        ax.set_xlabel('Day from 2026-01-01')
        ax.set_ylabel('Position Residual [km]')
        ax.set_title(f'{name}')
        ax.grid(True, alpha=0.3)
        ax.axhline(6000, color='red', linestyle='--', alpha=0.5,
                   label='6000 km threshold')
        ax.legend(fontsize=8)

    # Summary stats
    axes[1,1].axis('off')
    summary_text = "Residual Summary:\n\n"
    for name in ["Sun", "Earth", "Moon"]:
        max_r = df[f"{name}_eps_r_km"].max()
        mean_r = df[f"{name}_eps_r_km"].mean()
        status = "PASS" if max_r <= 6000 else "FAIL"
        summary_text += f"{name}: max={max_r:.1f} km, mean={mean_r:.1f} km [{status}]\n"
    axes[1,1].text(0.1, 0.5, summary_text, transform=axes[1,1].transAxes,
                   fontsize=10, family='monospace', verticalalignment='center')

    fig.suptitle('JPL Horizons Residual Comparison (2026)')
    plt.tight_layout()

    path = FIG_DIR / "residuals.png"
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


# ============================================================
# 图 4b: (t₀, r_p) 等值线图 (M6)
# ============================================================
def plot_contour_dv_t0_rp():
    """
    绘制 Δv_total 随 (t₀, r_p) 变化的等值线图。

    固定 r_m 为最优值附近的典型值，对 (t₀, r_p) 二维扫描，
    生成填充等值线图，展示最优发射窗口在参数空间中的位置。
    """
    print("Plotting (t0, rp) contour map...")
    from trajectory_optimizer import (
        R_MOON_MIN, R_P_MIN, R_P_MAX,
        earth_orbit_state, solve_patched_conic, solve_moon_flyby,
        MOON_ORBITAL_SPEED, V2_EARTH,
    )

    # 扫描参数
    n_t0 = 24   # 每半月一个采样点
    n_rp = 30   # r_p 方向精细采样
    t0_days = np.linspace(0, 360, n_t0, dtype=int)
    r_p_vals = np.linspace(R_P_MIN, R_P_MAX, n_rp)

    # 固定 r_m 为典型值
    r_m_fixed = 5000.0  # 典型近月距

    # 构建 Δv 矩阵
    dv_matrix = np.full((n_rp, n_t0), np.nan)

    for i, t0 in enumerate(t0_days):
        geo = earth_orbit_state(t0)
        r1 = geo['r1_km']
        v_e = geo['v_e_kms']

        for j, r_p in enumerate(r_p_vals):
            try:
                sol = solve_patched_conic(rp=float(r_p), r1=r1, v_e=v_e)
            except ValueError:
                continue

            # 月球借力贡献（简化：按 leading 侧估算）
            v_inf_moon = abs(sol.delta_v) + MOON_ORBITAL_SPEED
            flyby = solve_moon_flyby(r_m_fixed, v_inf_moon)
            moon_dv = flyby.get('delta_v_max', 0.0) if flyby.get('is_valid') else 0.0

            dv_earth = max(abs(sol.delta_v) - moon_dv * 0.5, 0.0)
            ms = moon_phase_state(t0)
            dv_residual = compute_physical_residual_dv(
                sol, ms, r_m_fixed, "leading", dv_earth, moon_dv,
            )['dv_residual_total_kms']
            v_inf_reentry = abs(sol.delta_v)
            dv_reentry = np.sqrt(V2_EARTH**2 + v_inf_reentry**2) - V2_EARTH

            # 约束检查
            if sol.rp < R_P_MIN or v_inf_reentry > 15.0:
                continue
            if sol.T_orbit / 86400.0 > 730.0:
                continue

            dv_matrix[j, i] = dv_earth + dv_residual + dv_reentry

    # 绘图
    fig, ax = plt.subplots(figsize=(11, 6))
    T0_mesh, RP_mesh = np.meshgrid(t0_days, r_p_vals / AU)

    # 填充等值线
    cf = ax.contourf(T0_mesh, RP_mesh, dv_matrix, levels=20,
                     cmap='RdYlBu_r', alpha=0.9)
    cs = ax.contour(T0_mesh, RP_mesh, dv_matrix, levels=8,
                    colors='black', linewidths=0.5, alpha=0.4)
    ax.clabel(cs, inline=True, fontsize=7, fmt='%.1f')

    cbar = fig.colorbar(cf, ax=ax, label=r'$\Delta v_{\mathrm{total}}$ [km/s]')
    cbar.ax.tick_params(labelsize=8)

    # 标注最小值位置
    min_idx = np.unravel_index(np.nanargmin(dv_matrix), dv_matrix.shape)
    ax.plot(t0_days[min_idx[1]], r_p_vals[min_idx[0]] / AU, 'k*',
            markersize=12, markeredgecolor='white', markeredgewidth=1.0,
            label=f'Min: {dv_matrix[min_idx]:.3f} km/s')

    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    ax.set_xticks(np.linspace(15, 345, 12))
    ax.set_xticklabels(months)
    ax.set_xlabel('Launch Date t₀ (2026)')
    ax.set_ylabel('Perihelion Distance r_p [AU]')
    ax.set_title(r'$\Delta v_{\mathrm{total}}(t_0, r_p)$ Contour Map ($r_m$ = 5000 km, leading side)')
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, alpha=0.15)

    plt.tight_layout()
    path = FIG_DIR / "contour_dv_t0_rp.png"
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


# ============================================================
# 图 5: MP4 轨道动画
# ============================================================
def render_orbit_animation(duration_sec=40, fps=20):
    """
    渲染轨道全景动画 MP4。

    使用 N 体积分器运行 1 年，下采样到 duration_sec * fps 帧，
    每帧绘制 Sun, Earth, Moon, Rocket 的位置轨迹。
    """
    print(f"Rendering animation ({duration_sec}s, {fps}fps)...")

    from nbody import make_sun_earth_moon_rocket

    bodies = make_sun_earth_moon_rocket()
    T = YEAR_SECONDS
    h = 3600.0
    n_frames = duration_sec * fps
    save_every = max(1, int(T / h) // n_frames)

    result = nbody_integrate(bodies, h=h, T=T, check_interval=save_every*10)

    # Downsample
    n_total = len(result.t)
    frame_indices = np.linspace(0, n_total-1, n_frames, dtype=int)

    fig, (ax_main, ax_zoom) = plt.subplots(1, 2, figsize=(14, 6.5),
                                            gridspec_kw={'width_ratios': [3, 1]})

    # Main view: heliocentric
    ax_main.set_xlim(-1.3*AU, 1.3*AU)
    ax_main.set_ylim(-1.3*AU, 1.3*AU)
    ax_main.set_aspect('equal')
    ax_main.set_title('Heliocentric View')
    ax_main.set_xlabel('X [km]')
    ax_main.set_ylabel('Y [km]')
    ax_main.grid(True, alpha=0.2)

    # Earth orbit circle
    theta = np.linspace(0, 2*np.pi, 500)
    ax_main.plot(AU*np.cos(theta), AU*np.sin(theta), '--', color='gray',
                 linewidth=0.6, alpha=0.4)

    # Zoom view: near Earth-Moon system
    ax_zoom.set_xlim(-6e5, 6e5)
    ax_zoom.set_ylim(-6e5, 6e5)
    ax_zoom.set_aspect('equal')
    ax_zoom.set_title('Earth-Moon Zoom')
    ax_zoom.set_xlabel('dX [km]')
    ax_zoom.set_ylabel('dY [km]')
    ax_zoom.grid(True, alpha=0.2)

    sun_scatter = ax_main.scatter([], [], s=120, color='orange', zorder=5)
    earth_scatter = ax_main.scatter([], [], s=30, color='green', zorder=4)
    moon_scatter = ax_main.scatter([], [], s=15, color='gray', zorder=4)
    rocket_scatter = ax_main.scatter([], [], s=5, color='red', zorder=5)

    earth_zoom = ax_zoom.scatter([], [], s=40, color='green', zorder=3)
    moon_zoom = ax_zoom.scatter([], [], s=20, color='gray', zorder=3)
    rocket_zoom = ax_zoom.scatter([], [], s=8, color='red', zorder=4)

    trail_main, = ax_main.plot([], [], 'r-', linewidth=0.3, alpha=0.3)
    trail_zoom, = ax_zoom.plot([], [], 'r-', linewidth=0.3, alpha=0.3)

    time_text = ax_main.text(0.02, 0.95, '', transform=ax_main.transAxes,
                             fontsize=10, family='monospace')

    rocket_trail_x = []
    rocket_trail_y = []
    max_trail = 500

    # Persistent zoom highlight markers (avoids per-frame artist leak)
    sun_zoom_hl, = ax_zoom.plot([], [], 'o', color='orange', markersize=25,
                                zorder=1, alpha=0.6)
    moon_zoom_hl, = ax_zoom.plot([], [], 'o', color='gray', markersize=20,
                                 zorder=1, alpha=0.6)
    sun_zoom_hl.set_visible(False)
    moon_zoom_hl.set_visible(False)

    # Event text & annotation markers for key events
    event_text = ax_main.text(0.02, 0.90, '', transform=ax_main.transAxes,
                              fontsize=9, family='monospace', color='red',
                              fontweight='bold')

    def init():
        return (sun_scatter, earth_scatter, moon_scatter, rocket_scatter,
                earth_zoom, moon_zoom, rocket_zoom, trail_main, trail_zoom,
                time_text, event_text, sun_zoom_hl, moon_zoom_hl)

    def animate(i):
        idx = frame_indices[i]

        sun_pos = result.positions["Sun"][idx]
        earth_pos = result.positions["Earth"][idx]
        moon_pos = result.positions["Moon"][idx]
        rocket_pos = result.positions["Rocket"][idx]

        sun_scatter.set_offsets([sun_pos])
        earth_scatter.set_offsets([earth_pos])
        moon_scatter.set_offsets([moon_pos])
        rocket_scatter.set_offsets([rocket_pos])

        # Dynamic zoom with key event detection
        r_rocket_sun = np.linalg.norm(rocket_pos - sun_pos)
        r_rocket_moon = np.linalg.norm(rocket_pos - moon_pos)
        r_rocket_earth = np.linalg.norm(rocket_pos - earth_pos)

        event_label = ''
        sun_zoom_hl.set_visible(False)
        moon_zoom_hl.set_visible(False)
        # Perihelion: rocket within 0.25 AU of Sun
        if r_rocket_sun < 0.25 * AU:
            zoom_half = 0.15 * AU
            ax_zoom.set_xlim(sun_pos[0] - zoom_half, sun_pos[0] + zoom_half)
            ax_zoom.set_ylim(sun_pos[1] - zoom_half, sun_pos[1] + zoom_half)
            ax_zoom.set_title('Perihelion Zoom (0.15 AU)')
            event_label = 'PERIHELION PASSAGE'
            sun_zoom_hl.set_data([sun_pos[0]], [sun_pos[1]])
            sun_zoom_hl.set_visible(True)
        # Moon flyby: rocket within 1.5x Moon SOI
        elif r_rocket_moon < 1.5 * 6.6e4:
            zoom_half = 1.2e5  # 120,000 km around Moon
            ax_zoom.set_xlim(moon_pos[0] - zoom_half, moon_pos[0] + zoom_half)
            ax_zoom.set_ylim(moon_pos[1] - zoom_half, moon_pos[1] + zoom_half)
            ax_zoom.set_title('Moon Flyby Zoom (120k km)')
            event_label = 'LUNAR GRAVITY ASSIST'
        # Earth departure/return: rocket near Earth
        elif r_rocket_earth < 5e5:
            zoom_half = 6e5
            ax_zoom.set_xlim(earth_pos[0] - zoom_half, earth_pos[0] + zoom_half)
            ax_zoom.set_ylim(earth_pos[1] - zoom_half, earth_pos[1] + zoom_half)
            ax_zoom.set_title('Earth-Moon Zoom')
        else:
            # Default: Earth-Moon view
            zoom_half = 6e5
            ax_zoom.set_xlim(earth_pos[0] - zoom_half, earth_pos[0] + zoom_half)
            ax_zoom.set_ylim(earth_pos[1] - zoom_half, earth_pos[1] + zoom_half)
            ax_zoom.set_title('Earth-Moon Zoom')

        # Zoom positions relative to zoom center
        zoom_center = np.array([ax_zoom.get_xlim()[0] + zoom_half,
                                 ax_zoom.get_ylim()[0] + zoom_half])
        earth_zoom.set_offsets([earth_pos - zoom_center])
        moon_zoom.set_offsets([moon_pos - zoom_center])
        rocket_zoom.set_offsets([rocket_pos - zoom_center])

        # Trail
        rocket_trail_x.append(rocket_pos[0])
        rocket_trail_y.append(rocket_pos[1])
        if len(rocket_trail_x) > max_trail:
            rocket_trail_x.pop(0)
            rocket_trail_y.pop(0)
        trail_main.set_data(rocket_trail_x, rocket_trail_y)
        trail_zoom.set_data(
            [x - zoom_center[0] for x in rocket_trail_x[-max_trail//2:]],
            [y - zoom_center[1] for y in rocket_trail_y[-max_trail//2:]],
        )

        t_days = result.t[idx] / 86400.0
        time_text.set_text(f'Day {t_days:.0f} / 365')
        event_text.set_text(event_label)

        return (sun_scatter, earth_scatter, moon_scatter, rocket_scatter,
                earth_zoom, moon_zoom, rocket_zoom, trail_main, trail_zoom,
                time_text, event_text, sun_zoom_hl, moon_zoom_hl)

    ani = animation.FuncAnimation(
        fig, animate, init_func=init, frames=n_frames,
        interval=1000/fps, blit=True,
    )

    mp4_path = OUTPUT_DIR / "orbit_animation.mp4"
    try:
        ani.save(str(mp4_path), writer='ffmpeg', fps=fps, dpi=150)
        print(f"  Saved: {mp4_path}")
    except Exception as e:
        print(f"  [WARNING] ffmpeg not available, saving GIF instead: {e}")
        gif_path = OUTPUT_DIR / "orbit_animation.gif"
        ani.save(str(gif_path), writer='pillow', fps=10, dpi=100)
        print(f"  Saved: {gif_path}")

    plt.close(fig)


# ============================================================
# 主入口
# ============================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Visualization generator (Phase 5)")
    parser.add_argument("--full", action="store_true",
                        help="Include animation rendering (requires ffmpeg)")
    parser.add_argument("--animate-only", action="store_true",
                        help="Only render animation")
    args = parser.parse_args()

    if args.animate_only:
        render_orbit_animation(duration_sec=30, fps=15)
        return

    print("=" * 60)
    print("Generating static plots...")
    print("=" * 60)

    plot_orbit_trajectory()
    plot_energy_conservation()
    plot_dv_vs_launch_date()
    plot_contour_dv_t0_rp()
    plot_residuals()

    if args.full:
        print("\nRendering animation...")
        render_orbit_animation(duration_sec=40, fps=20)

    print(f"\nAll figures saved to: {FIG_DIR}")
    print(f"Animation saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()