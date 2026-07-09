# -*- coding: utf-8 -*-
"""
patched_conic.py — 钱学森拼接圆锥曲线解析算法 (阶段 3 / M1 & M4)
===============================================================
将 report.tex 中 §3–§5 的步骤一至步骤六完整编码。

核心功能：
  1. 给定近日距 r_p 和地球轨道参数，计算椭圆轨道根数与 Δv
  2. 月球借力 (M4)：在月球引力作用球内解析月球双曲线飞越
  3. 基准测试：r_p = 0.2 AU 时与原算例偏差 ≤ 0.1%

理论参考：
  - 钱学森《星际航行概论》(2008) 第5-6章
  - Vallado §12.4 (patched conic / SOI matching)
  - report.tex 公式体系 (§3–§5)

坐标系与单位：
  - J2000 黄道 2D 投影
  - 位置: km, 速度: km/s, 时间: s

作者：Claude Code (deepseek-v4-pro) + 用户审校
日期：2026-06-17
"""

import numpy as np
from typing import Tuple, Dict, Optional
from dataclasses import dataclass

# ============================================================
# 1. 物理常数
# ============================================================
G_SUN = 1.32712440018e11      # 太阳引力常数 [km³/s²]
G_EARTH = 3.986004354e5       # 地球引力常数 [km³/s²]
G_MOON = 4.902800118e3        # 月球引力常数 [km³/s²]
AU = 1.495978707e8            # 天文单位 [km]
V_EARTH = 29.783              # 地球公转速度 [km/s]
V2_EARTH = 11.18              # 地球表面第二宇宙速度 [km/s]
R_SUN = 6.957e5               # 太阳半径 [km]
R_MOON = 1737.4               # 月球半径 [km]
R_MOON_MIN = 1838.0            # 不撞月下限 (R_moon + 100, 与 PROJECT_SPEC 一致) [km]
R_EARTH_SOI = 9.24e5          # 地球引力作用球半径 (~9.24×10⁵ km)
MOON_SOI = 6.6e4              # 月球引力作用球半径 [km]
MOON_SEMI_MAJOR = 3.844e5     # 月球轨道半长轴 [km]
MOON_ORBITAL_SPEED = 1.022    # 月球绕地速度 [km/s]
YEAR_DAYS = 365.25            # 地球公转周期 [天]


# ============================================================
# 2. 数据容器
# ============================================================
@dataclass
class PatchedConicSolution:
    """
    拼接圆锥曲线法求解结果。
    """
    r1: float                    # 地球轨道半径 [km] (= AU)
    rp: float                    # 近日距 [km]
    a: float                     # 转移椭圆半长轴 [km]
    e: float                     # 转移椭圆偏心率
    p: float                     # 转移椭圆半通径 [km]
    v1: float                    # 日心速度（出发/返回点）[km/s]
    delta_v: float               # 日心速度增量 Δv [km/s]
    v_launch: float              # 地面发射速度 [km/s]
    T_orbit: float               # 轨道周期 [s]
    T_orbit_days: float          # 轨道周期 [天]
    delta_t: float               # 单程飞行时间 [s]
    delta_t_days: float          # 单程飞行时间 [天]
    v_inf_return: float          # 再入超速 [km/s]
    v_reentry: float             # 再入速度 [km/s]
    # 月球借力增量 (M4)
    moon_flyby_delta_v: float = 0.0  # 月球借力提供的额外 Δv [km/s]
    moon_rp: float = 0.0             # 近月距 [km]
    moon_bend_angle: float = 0.0     # 月球双曲线偏转角 [rad]


# ============================================================
# 3. 核心解析算法 (report.tex §3–§5, 步骤一至六)
# ============================================================
def solve_patched_conic(
    rp: float,
    r1: float = AU,
    K_s: float = G_SUN,
    v_e: float = V_EARTH,
    v2: float = V2_EARTH,
) -> PatchedConicSolution:
    """
    钱学森拼接圆锥曲线法核心求解器。

    解析步骤 (对应 report.tex)：
      步骤一：已知参数  r1, v_e, v2
      步骤二：选定近日距 r_p
      步骤三：计算椭圆轨道参数 a, e, p
      步骤四：由活力公式求出发日心速度和 Δv
      步骤五：求地面发射速度
      步骤六：求飞行时间

    Args:
        rp: 近日距 [km]（须满足 R_SUN < rp < r1）
        r1: 地球轨道半径 [km]，默认 1 AU
        K_s: 太阳向心力常数 = GM_sun [km³/s²]
        v_e: 地球公转速度 [km/s]
        v2: 地球表面第二宇宙速度 [km/s]

    Returns:
        PatchedConicSolution
    """
    # === 公式验证 ===
    if rp <= R_SUN:
        raise ValueError(f"rp={rp:.2e} km ≤ R_SUN={R_SUN:.2e} km — 火箭撞日!")
    if rp >= r1:
        raise ValueError(f"rp={rp:.2e} km ≥ r1={r1:.2e} km — 轨道无内侧近日距!")

    # === 步骤三：椭圆轨道参数 [report.tex eq.(20)-(22)] ===
    # a = (r1 + rp) / 2
    a = (r1 + rp) / 2.0

    # e = (r1 - rp) / (r1 + rp)
    e = (r1 - rp) / (r1 + rp)

    # p = 2 * r1 * rp / (r1 + rp)
    p = (2.0 * r1 * rp) / (r1 + rp)

    # === 步骤四：日心速度与 Δv [report.tex eq.(23)-(24)] ===
    # v1 = v_e * sqrt(2*rp / (r1 + rp))
    v1 = v_e * np.sqrt(2.0 * rp / (r1 + rp))

    # Δv = v1 - v_e = v_e * (sqrt(2*rp/(r1+rp)) - 1)
    # 负值表示向地球公转反方向减速发射
    delta_v = v1 - v_e

    # === 步骤五：地面发射速度 [report.tex eq.(25)] ===
    # v_launch = sqrt(v2² + |Δv|²)
    v_launch = np.sqrt(v2 ** 2 + abs(delta_v) ** 2)

    # === 步骤六：飞行时间 [report.tex eq.(26)-(29)] ===
    # 轨道周期 T = 2π * sqrt(a³/K_s)
    T_orbit = 2.0 * np.pi * np.sqrt(a ** 3 / K_s)

    # 单程飞行：从远日点到近日点 = T/2
    delta_t = T_orbit / 2.0

    # === 再入分析 [report.tex §4.8] ===
    v_inf_return = abs(delta_v)  # 返回双曲线超速 ≈ |Δv|
    v_reentry = np.sqrt(v2 ** 2 + v_inf_return ** 2)

    return PatchedConicSolution(
        r1=r1,
        rp=rp,
        a=a,
        e=e,
        p=p,
        v1=v1,
        delta_v=delta_v,
        v_launch=v_launch,
        T_orbit=T_orbit,
        T_orbit_days=T_orbit / 86400.0,
        delta_t=delta_t,
        delta_t_days=delta_t / 86400.0,
        v_inf_return=v_inf_return,
        v_reentry=v_reentry,
    )


# ============================================================
# 4. 月球借力解析计算 (M4)
# ============================================================
def solve_moon_flyby(
    r_p_moon: float,
    v_inf_moon: float,
    mu_moon: float = G_MOON,
    R_moon: float = R_MOON,
    soi_moon: float = MOON_SOI,
) -> Dict[str, float]:
    """
    月球双曲线飞越的解析计算。

    物理原理（参考 Vallado §12.4 方法）：
      火箭以双曲线超速 v∞ 进入月球引力作用球（SOI），
      在月心坐标系中沿双曲线轨道运动。近月距 r_p_moon 决定
      偏转角 δ (bend angle) 和速度增量 ΔVmoon。

      双曲线轨道：
        e_hyper = 1 + r_p_moon * v∞² / μ_moon
        δ = 2 * arcsin(1 / e_hyper)   (偏转角)
        Δv_moon = 2 * v∞ * sin(δ/2)   (最大可能借力增量)

    几何约束：
      - 近月距 r_p_moon ≥ R_MOON_MIN = 1838 km（不撞月）
      - 进入 SOI 时半径 ≈ soi_moon

    Args:
        r_p_moon: 近月距 [km]（≥ R_moon + 100）
        v_inf_moon: 火箭相对月球的超速 [km/s]
        mu_moon: 月球引力常数 [km³/s²]
        R_moon: 月球半径 [km]
        soi_moon: 月球 SOI 半径 [km]

    Returns:
        dict: {
            'eccentricity': 双曲线偏心率,
            'bend_angle_deg': 偏转角 [deg],
            'delta_v_max': 最大可用借力 Δv [km/s],
            'soi_radius': SOI 半径 [km],
            'is_valid': 是否满足物理约束,
        }
    """
    if r_p_moon < R_MOON_MIN:
        return {
            'eccentricity': np.nan,
            'bend_angle_deg': np.nan,
            'delta_v_max': np.nan,
            'soi_radius': soi_moon,
            'is_valid': False,
            'error': f'r_p_moon={r_p_moon:.0f} km < R_MOON_MIN={R_MOON_MIN:.0f} km',
        }

    if v_inf_moon < 0.1:
        return {
            'eccentricity': 1.0,
            'bend_angle_deg': 0.0,
            'delta_v_max': 0.0,
            'soi_radius': soi_moon,
            'is_valid': False,
            'error': f'v_inf_moon={v_inf_moon:.3f} km/s too low for meaningful flyby',
        }

    # 双曲线偏心率: e = 1 + r_p * v∞² / μ
    e_hyper = 1.0 + r_p_moon * v_inf_moon ** 2 / mu_moon

    # 偏转角: δ = 2 * arcsin(1/e)（双曲线渐近线夹角）
    if e_hyper <= 1.0:
        bend_angle = 0.0
    else:
        bend_angle = 2.0 * np.arcsin(1.0 / e_hyper)

    # 最大速度增量：将 v∞ 矢量旋转 δ 角
    # Δv_max = 2 * v∞ * sin(δ/2)
    delta_v_max = 2.0 * v_inf_moon * np.sin(bend_angle / 2.0)

    # SOI 进入/退出时的速度矢量方向变化
    # 对于出射方向的最优借力，Δv 全加在日心速度方向
    return {
        'eccentricity': e_hyper,
        'bend_angle_deg': np.degrees(bend_angle),
        'bend_angle_rad': bend_angle,
        'delta_v_max': delta_v_max,
        'soi_radius': soi_moon,
        'is_valid': True,
    }


def apply_moon_flyby(
    sol: PatchedConicSolution,
    r_p_moon: float,
    v_inf_moon: Optional[float] = None,
) -> PatchedConicSolution:
    """
    将月球借力增量应用到已有的日心轨道解中。

    当火箭从地球出发时，月球可提供额外的 Δv。
    若火箭朝月球前方飞行（leading side），可获得减速增量，
    有助于向太阳方向降低近日距。

    协调系统转换（日心 ↔ 地心 ↔ 月心）：
      1. 火箭脱离地球 SOI 后，v_∞_earth = |Δv|
      2. 在地心系中，月球相对速度为 v_moon_orbit ≈ 1.022 km/s
      3. 火箭相对月球的速度为 v_rocket_moon = v_rocket_geo - v_moon_geo
      4. 在月心双曲线飞越后，出射速度相同大小，方向偏转
      5. 转换回地心系，再转换回日心系

    简化处理（2D 共面假设）：
      - 最优借力发生在火箭轨迹平面与月球轨道平面重合时
      - leading side: 火箭从月球前方飞越 → 减速 → 近日距减小
      - trailing side: 火箭从月球后方飞越 → 加速 → 近日距增大

    Args:
        sol: 原始拼接圆锥曲线解
        r_p_moon: 近月距 [km]
        v_inf_moon: 火箭相对月球的超速 [km/s]。
                    若为 None，自动估算为 |Δv| + v_moon_orbit

    Returns:
        更新后的 PatchedConicSolution（含月球借力 Δv）
    """
    if v_inf_moon is None:
        # 火箭相对月球的速度 ≈ |Δv|（日心不足部分）
        # 加上月球绕地速度（最优情况下同向）
        v_inf_moon = abs(sol.delta_v) + MOON_ORBITAL_SPEED

    flyby = solve_moon_flyby(r_p_moon, v_inf_moon)

    if not flyby['is_valid']:
        print(f"[WARNING] Moon flyby invalid: {flyby.get('error', 'unknown')}")
        return sol

    # 更新解中的月球借力信息
    sol.moon_flyby_delta_v = flyby['delta_v_max']
    sol.moon_rp = r_p_moon
    sol.moon_bend_angle = flyby['bend_angle_rad']

    return sol


# ============================================================
# 5. 基准测试 (M1)
# ============================================================
def test_qian_xuesen_baseline():
    """
    钱学森原算例基准测试。

    原算例（report.tex §5）:
      r_p = 0.2 AU = 2.99×10⁷ km
      → a = 0.6 AU, e = 0.6667, p = 0.333 AU
      → v1 = 17.21 km/s, Δv = -12.59 km/s
      → v_launch = 16.84 km/s
      → T = 169.8 天

    验收指标：与原算例偏差 ≤ 0.1%
    """
    print("=" * 60)
    print("Test P1: Qian Xuesen Baseline (rp = 0.2 AU)")
    print("=" * 60)

    rp = 0.2 * AU
    sol = solve_patched_conic(rp=rp)

    # 原算例参考值
    ref = {
        'a_AU': 0.6,
        'e': 0.6666667,
        'p_AU': 1.0/3.0,  # exact: 2*1*0.2/(1+0.2) = 1/3
        'v1_kms': 17.21,
        'delta_v_kms': -12.59,
        'v_launch_kms': 16.84,
        'T_days': 169.8,
        'delta_t_days': 84.9,
    }

    results = {
        'a_AU': sol.a / AU,
        'e': sol.e,
        'p_AU': sol.p / AU,
        'v1_kms': sol.v1,
        'delta_v_kms': sol.delta_v,
        'v_launch_kms': sol.v_launch,
        'T_days': sol.T_orbit_days,
        'delta_t_days': sol.delta_t_days,
    }

    print(f"  {'Parameter':<20} {'Computed':<14} {'Reference':<14} {'Deviation':<12}")
    print(f"  {'-'*60}")
    all_ok = True
    for key in ref:
        comp = results[key]
        ref_val = ref[key]
        dev = abs(comp - ref_val) / abs(ref_val) * 100 if ref_val != 0 else abs(comp)
        status = "OK" if dev <= 0.1 else "FAIL"
        if dev > 0.1:
            all_ok = False
        print(f"  {key:<20} {comp:<14.6f} {ref_val:<14.6f} {dev:<10.5f}% [{status}]")

    assert all_ok, "Baseline deviation > 0.1% — 解析公式需核查!"

    # 额外验证：物理一致性
    # 1. a = (r1+rp)/2
    assert abs(sol.a - (AU + rp) / 2.0) < 1e-3, "半长轴公式不满足"
    # 2. 能量：v1²/2 - K_s/r1 = -K_s/(2a)（Vis-viva）
    E_vis = 0.5 * sol.v1 ** 2 - G_SUN / AU
    E_expected = -G_SUN / (2 * sol.a)
    assert abs(E_vis - E_expected) / abs(E_expected) < 1e-4, \
        f"Vis-viva equation mismatch: E_vis={E_vis:.3f}, E_expected={E_expected:.3f}"
    # 3. 近日距不撞日
    assert sol.rp > R_SUN, "rp < R_SUN — 火箭撞日!"

    print(f"\n  [PASSED] All parameters within 0.1% of Qian's reference.\n")
    return True


def test_moon_flyby():
    """测试 2: 月球借力解析"""
    print("=" * 60)
    print("Test P2: Moon Flyby Analytics")
    print("=" * 60)

    # 典型值：r_p_moon = 2000 km, v_inf = 3 km/s
    flyby = solve_moon_flyby(r_p_moon=2000.0, v_inf_moon=3.0)

    print(f"  r_p_moon = 2000 km, v_inf = 3.0 km/s")
    print(f"  e_hyper = {flyby['eccentricity']:.6f}")
    print(f"  bend_angle = {flyby['bend_angle_deg']:.3f} deg")
    print(f"  delta_v_max = {flyby['delta_v_max']:.4f} km/s")
    print(f"  is_valid = {flyby['is_valid']}")

    assert flyby['is_valid'], "Valid flyby marked as invalid"
    assert flyby['eccentricity'] > 1.0, "Hyperbola must have e > 1"
    assert flyby['bend_angle_deg'] > 0, "Non-zero bend angle for e>1"
    assert flyby['delta_v_max'] < 2.0 * 3.0, "Δv_max ≤ 2*v∞"

    # 撞月球测试
    flyby_invalid = solve_moon_flyby(r_p_moon=1700.0, v_inf_moon=1.0)
    assert not flyby_invalid['is_valid'], "Should reject sub-R_moon distance"

    print(f"  [PASSED] Moon flyby analytics verified.\n")
    return True


def test_combined_conic_with_moon():
    """测试 3: 钱学森解 + 月球借力组合"""
    print("=" * 60)
    print("Test P3: Combined Patched Conic + Moon Flyby")
    print("=" * 60)

    rp = 0.2 * AU
    sol = solve_patched_conic(rp=rp)
    sol_with_moon = apply_moon_flyby(sol, r_p_moon=5000.0)

    print(f"  Without moon: Δv_total  = {abs(sol.delta_v):.4f} km/s")
    print(f"  With moon:    Δv_total  = {abs(sol_with_moon.delta_v) + sol_with_moon.moon_flyby_delta_v:.4f} km/s")
    print(f"  Moon flyby Δv contribution = {sol_with_moon.moon_flyby_delta_v:.4f} km/s")
    print(f"  Moon bend angle = {np.degrees(sol_with_moon.moon_bend_angle):.2f} deg")

    # 物理约束验证
    assert sol_with_moon.moon_rp >= R_MOON_MIN, "Moon periapsis violates constraint"
    print(f"  [PASSED] Combined solution valid.\n")
    return True


# ============================================================
# 5b. 月球借力数值仿真 (M4 数值部分)
# ============================================================
def simulate_moon_flyby_numerical(
    r_p_moon: float,
    v_inf_moon: float,
    h: float = 10.0,
    soi_moon: float = MOON_SOI,
    mu_moon: float = G_MOON,
) -> Dict[str, float]:
    """
    月球双曲线飞越的数值N体仿真。

    在月心坐标系中用 Velocity-Verlet 积分器模拟火箭从 SOI 边界
    进入、经过近月点、再从 SOI 边界退出的全过程。
    从数值轨迹中提取实际偏转角 δ 和速度增量 Δv，
    与解析公式（solve_moon_flyby）对比验证。

    仿真设置：
      - 参考系：月心 2D 坐标系
      - 初始位置：SOI 边界处，x = -soi_moon, y = r_p_moon (瞄准距)
      - 初始速度：沿 +x 方向，大小为 v_inf_moon
      - 积分：Velocity-Verlet, h=10s，直至火箭再次到达 SOI 边界

    Args:
        r_p_moon: 近月距 [km]
        v_inf_moon: 双曲线超速 [km/s]
        h: 积分步长 [s]
        soi_moon: 月球 SOI 半径 [km]
        mu_moon: 月球引力常数 [km³/s²]

    Returns:
        dict: {
            'bend_angle_deg': 数值实测偏转角 [deg],
            'bend_angle_analytical_deg': 解析公式偏转角 [deg],
            'delta_v_numerical': 数值 Δv [km/s],
            'delta_v_analytical': 解析 Δv [km/s],
            'bend_angle_rel_err': 偏转角相对偏差,
            'delta_v_rel_err': Δv 相对偏差,
            'trajectory': (r_ary, v_ary) 轨迹数组,
        }
    """
    from nbody import Body, velocity_verlet_step

    if r_p_moon < R_MOON_MIN:
        raise ValueError(f"r_p_moon={r_p_moon:.0f} < R_MOON_MIN={R_MOON_MIN:.0f} km")

    # --- 构造初始状态（月心坐标系）---
    # 由解析双曲线公式计算撞击参数 b（impact parameter）
    #   e = 1 + r_p·v∞²/μ
    #   b = r_p·√((e+1)/(e-1))
    # 在远处（d_start >> b），火箭位置 ≈ (-d_start, b)，速度 ≈ (v∞, 0)
    e_hyper = 1.0 + r_p_moon * v_inf_moon**2 / mu_moon
    b_impact = r_p_moon * np.sqrt((e_hyper + 1.0) / max(e_hyper - 1.0, 1e-12))

    # 从远处开始积分，确保初始/最终速度方向接近渐近线方向
    d_start = max(5.0 * soi_moon, 10.0 * b_impact)
    x0 = -d_start
    y0 = b_impact
    vx0 = v_inf_moon
    vy0 = 0.0

    moon = Body(
        name="Moon",
        mu=mu_moon,
        r=np.array([0.0, 0.0]),
        v=np.array([0.0, 0.0]),
        massless=False,
    )
    rocket = Body(
        name="Rocket",
        mu=0.0,
        r=np.array([x0, y0]),
        v=np.array([vx0, vy0]),
        massless=True,
    )

    bodies = [moon, rocket]

    # --- 积分至火箭穿过近月点并再次远离 ---
    max_steps = 800000
    r_traj = [rocket.r.copy()]
    v_traj = [rocket.v.copy()]
    v_in = rocket.v.copy()  # 进入速度（月心系，≈渐近线方向）

    # 跟踪是否已过近月点
    r_min = np.linalg.norm(rocket.r)
    passed_periapsis = False

    for _ in range(max_steps):
        velocity_verlet_step(bodies, h)
        r = np.linalg.norm(rocket.r)
        r_traj.append(rocket.r.copy())
        v_traj.append(rocket.v.copy())

        # 检测是否经过近月点
        if r < r_min:
            r_min = r
        elif r > r_min * 1.1 and not passed_periapsis:
            passed_periapsis = True

        # 退出条件：已过近月点且距离回到初始距离
        if passed_periapsis and r >= d_start:
            break

    # 出射速度（≈渐近线方向）
    v_out = rocket.v.copy()

    # --- 从数值轨迹提取偏转角 ---
    dot_vv = np.dot(v_in, v_out)
    norm_v = np.linalg.norm(v_in) * np.linalg.norm(v_out)
    cos_bend = np.clip(dot_vv / max(norm_v, 1e-30), -1.0, 1.0)
    bend_angle_num = np.arccos(cos_bend)
    delta_v_num = np.linalg.norm(v_out - v_in)

    # --- 解析公式对比 ---
    analytical = solve_moon_flyby(r_p_moon, v_inf_moon, mu_moon, R_MOON, soi_moon)
    bend_angle_ana = analytical.get('bend_angle_rad', 0.0)
    delta_v_ana = analytical.get('delta_v_max', 0.0)

    bend_rel_err = abs(bend_angle_num - bend_angle_ana) / max(abs(bend_angle_ana), 1e-12)
    dv_rel_err = abs(delta_v_num - delta_v_ana) / max(abs(delta_v_ana), 1e-12)

    return {
        'bend_angle_deg': float(np.degrees(bend_angle_num)),
        'bend_angle_analytical_deg': float(np.degrees(bend_angle_ana)),
        'delta_v_numerical': float(delta_v_num),
        'delta_v_analytical': float(delta_v_ana),
        'bend_angle_rel_err': float(bend_rel_err),
        'delta_v_rel_err': float(dv_rel_err),
        'trajectory': (np.array(r_traj), np.array(v_traj)),
    }


def test_numerical_moon_flyby():
    """
    测试 4: 月球借力数值仿真 vs 解析公式对比 (M4 两套实现验证)

    验收指标：
      - 偏转角 δ 偏差 ≤ 2%（数值 vs 解析）
      - Δv 偏差 ≤ 2%
    """
    print("=" * 60)
    print("Test P4: Numerical vs Analytical Moon Flyby (M4)")
    print("=" * 60)

    # 测试多个近月距和超速组合
    test_cases = [
        (2000.0, 3.0),
        (5000.0, 2.0),
        (10000.0, 4.0),
        (3000.0, 1.5),
    ]

    all_ok = True
    for r_p, v_inf in test_cases:
        result = simulate_moon_flyby_numerical(r_p_moon=r_p, v_inf_moon=v_inf)
        delta_bend = result['bend_angle_rel_err'] * 100
        delta_dv = result['delta_v_rel_err'] * 100
        status_bend = "OK" if delta_bend <= 2.0 else "FAIL"
        status_dv = "OK" if delta_dv <= 2.0 else "FAIL"
        if delta_bend > 2.0 or delta_dv > 2.0:
            all_ok = False

        print(f"  r_p={r_p:.0f}km, v_inf={v_inf:.1f}km/s:")
        print(f"    δ  (numerical): {result['bend_angle_deg']:.4f} deg")
        print(f"    δ  (analytical): {result['bend_angle_analytical_deg']:.4f} deg")
        print(f"    δ  rel err: {delta_bend:.4f}% [{status_bend}]")
        print(f"    Δv (numerical): {result['delta_v_numerical']:.4f} km/s")
        print(f"    Δv (analytical): {result['delta_v_analytical']:.4f} km/s")
        print(f"    Δv rel err: {delta_dv:.4f}% [{status_dv}]")

    assert all_ok, "Numerical vs analytical moon flyby deviation > 2%"
    print(f"\n  [PASSED] Numerical simulation matches analytical formula within 2%.\n")
    return True


# ============================================================
# 6. 主入口
# ============================================================
def run_all_tests():
    """运行阶段 3 单元测试"""
    tests = [
        test_qian_xuesen_baseline,
        test_moon_flyby,
        test_combined_conic_with_moon,
        test_numerical_moon_flyby,
    ]
    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}\n")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed, {passed + failed} total")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    run_all_tests()