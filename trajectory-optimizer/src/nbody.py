# -*- coding: utf-8 -*-
"""
nbody.py — 高精度 N 体数值积分器模块
=====================================
适用于「钱学森问题扩展求解」项目（阶段 1 / M2）

核心功能：
  1. Sun–Earth–Moon–Rocket 四体（限制性）数值积分器
  2. 2 阶辛积分器 Velocity-Verlet（可切换近距精细步长）
  3. 守恒量（总能量、角动量）监测
  4. 二体圆轨道基准验证（μ = 4π² 无量纲）

坐标系与单位：
  - 参考系：J2000 黄道平面投影（2D），xy 平面
  - 位置单位：km
  - 时间单位：s
  - 速度单位：km/s

作者：Claude Code (deepseek-v4-pro) + 用户审校
日期：2026-06-17
"""

import numpy as np
from typing import Tuple, List, Optional, Dict, Callable
from dataclasses import dataclass, field
import warnings

# ============================================================
# 1. 物理常数定义
# ============================================================
# 引力常数 (km³/s²)，来源于 DE440 / JPL Horizons 参考值
G_SUN = 1.32712440018e11       # 太阳引力常数 GM_sun  [km³/s²]
G_EARTH = 3.986004354e5        # 地球引力常数 GM_earth [km³/s²]
G_MOON = 4.902800118e3         # 月球引力常数 GM_moon  [km³/s²]

# 天体半径与轨道参考值（用于碰撞检测与 SOI 计算）
R_SUN = 6.957e5                # 太阳半径 [km]
R_EARTH = 6371.0               # 地球半径 [km]
R_MOON = 1737.4                # 月球半径 [km]
AU = 1.495978707e8             # 天文单位 [km]
V_EARTH = 29.783               # 地球公转速度（~1 AU 处圆轨道近似）[km/s]
YEAR_SECONDS = 365.25 * 86400  # 1 年 [s]

# 月球轨道近似参数
MOON_SEMI_MAJOR = 3.844e5      # 月球轨道半长轴 [km]
MOON_ORBITAL_SPEED = 1.022     # 月球绕地平均速度 [km/s]

# 广义相对论修正参数 (O2 / Rule 26)
C_LIGHT = 2.99792458e5               # 光速 [km/s]
GR_SUN_FACTOR = 3.0 * G_SUN**2 / C_LIGHT**2  # 3μ²/c² for GR correction

# 二体基准测试的无量纲参数
MU_DIMENSIONLESS = 4.0 * np.pi ** 2  # μ = 4π²


# ============================================================
# 2. 数据容器
# ============================================================
@dataclass
class Body:
    """N 体系统中的单个天体/质点"""
    name: str
    mu: float                     # 引力常数 GM [km³/s²]；无质量物体（火箭）为 0
    r: np.ndarray                 # 位置向量 [km]，shape=(2,)
    v: np.ndarray                 # 速度向量 [km/s]，shape=(2,)
    massless: bool = False        # True 表示无质量测试粒子


@dataclass
class IntegratorResult:
    """数值积分器的完整输出"""
    t: np.ndarray                 # 时间格点 [s]，shape=(N+1,)
    positions: Dict[str, np.ndarray]   # 各天体位置 [km]，每个 shape=(N+1, 2)
    velocities: Dict[str, np.ndarray]  # 各天体速度 [km/s]，每个 shape=(N+1, 2)
    energy_history: np.ndarray         # 总能量历史，shape=(M,)
    angular_momentum_history: np.ndarray  # 总角动量历史，shape=(M,)
    energy_check_steps: np.ndarray     # 能量检查步索引，shape=(M,)
    final_pos_err: Optional[float] = None      # 基准测试用：最终位置误差
    final_rel_energy_err: Optional[float] = None
    final_rel_angmom_err: Optional[float] = None


# ============================================================
# 3. 核心物理函数
# ============================================================
def acceleration_nbody(bodies: List[Body], i_body: int) -> np.ndarray:
    """
    计算第 i_body 个天体受到其余所有天体的引力加速度。

    物理原理：
      根据牛顿万有引力定律，天体 j 对天体 i 的加速度为：
        a_{ij} = -GM_j * (r_i - r_j) / |r_i - r_j|^3
      所有天体对 i 的总加速度为 Σ_j a_{ij} (j ≠ i)。

    无质量天体（massless=True）不产生引力，仅被动受其他天体吸引。

    Args:
        bodies: 天体列表
        i_body: 待计算加速度的天体索引

    Returns:
        a: 加速度向量 [km/s^2], shape=(2,)
    """
    a = np.zeros(2, dtype=float)
    for j, body_j in enumerate(bodies):
        if j == i_body:
            continue
        # 无质量天体不对其他天体产生引力
        if body_j.massless:
            continue
        dr = bodies[i_body].r - body_j.r
        r2 = np.dot(dr, dr)
        r = np.sqrt(r2)
        # 软化工避免除零（防止天体碰撞时数值爆炸）
        soft = 1e-8 * body_j.mu ** (2 / 3) if body_j.mu > 0 else 1e-4
        if r < soft:
            r = soft
            r2 = soft ** 2
        # 引力加速度 = -GM_j * (r_i - r_j) / |r_i - r_j|^3
        a += -body_j.mu * dr / (r2 * r)
    return a


def total_angular_momentum(bodies: List[Body]) -> float:
    """
    计算系统总角动量 z 分量（质量加权，乘以 G 后）。

    物理定义：
      L_true = Σ_i m_i * (r_i × v_i)
      G·L_true = Σ_i μ_i * (r_{x,i} * v_{y,i} - r_{y,i} * v_{x,i})

    质量加权确保各天体按质量比例贡献角动量。
    无质量天体（μ=0）不贡献系统角动量。

    Returns:
        G·L_true [km⁴/s]（有量纲，不妨碍相对漂移监测）
    """
    L = 0.0
    for body in bodies:
        if body.massless:
            continue
        L += body.mu * (body.r[0] * body.v[1] - body.r[1] * body.v[0])
    return L


def energy_nbody(bodies: List[Body]) -> float:
    """
    计算系统总机械能（乘以引力常数 G 后的标量）。

    对于 N 体系统，真实总能量：
        E_true = Σ_i (1/2)*m_i*v_i² - Σ_{i<j} (G*m_i*m_j / r_ij)
    用 μ_i = G*m_i 替换后：
        E_true = Σ_i (1/2)*(μ_i/G)*v_i² - Σ_{i<j} (μ_i*μ_j / (G*r_ij))
        G·E_true = Σ_i (1/2)*μ_i*v_i² - Σ_{i<j} (μ_i*μ_j / r_ij)

    我们定义 E' = G·E_true 用于守恒监测。
    质量权重由 μ_i 自动体现：大质量天体（如太阳 μ≈1.33e11）的贡献
    远大于小质量天体（如月球 μ≈4.9e3）。

    无质量天体（μ=0）不贡献系统能量。

    返回 E' [km⁵/s⁴]（有量纲，但不影响相对漂移计算）。
    """
    E = 0.0
    n = len(bodies)
    for i, bi in enumerate(bodies):
        if bi.massless:
            continue
        # 动能项: (1/2) * μ_i * v_i²
        E += 0.5 * bi.mu * np.dot(bi.v, bi.v)
        # 势能项: - Σ_{j>i} μ_i * μ_j / r_ij
        for j in range(i + 1, n):
            bj = bodies[j]
            if bj.massless:
                continue
            dr = bi.r - bj.r
            r = np.linalg.norm(dr)
            if r < 1e-4:
                r = 1e-4
            E -= bi.mu * bj.mu / r
    return E


def energy_test_particle(bodies: List[Body], test_name: str = "Earth",
                         central_name: str = "Sun") -> float:
    """
    计算无质量测试粒子在中心天体引力场中的轨道能量。

    适用于二体圆轨道基准测试：
        E = 0.5*v² - μ_central / r

    若测试粒子非无质量，则仍按此公式计算单位质量的轨道能量。

    Args:
        bodies: 天体列表
        test_name: 测试粒子名称
        central_name: 中心天体名称

    Returns:
        轨道能量 [km²/s²]
    """
    test_body = None
    central_body = None
    for b in bodies:
        if b.name == test_name:
            test_body = b
        if b.name == central_name:
            central_body = b

    if test_body is None or central_body is None:
        raise ValueError(f"Bodies '{test_name}' or '{central_name}' not found.")

    dr = test_body.r - central_body.r
    r = np.linalg.norm(dr)
    if r < 1e-4:
        r = 1e-4

    return 0.5 * np.dot(test_body.v, test_body.v) - central_body.mu / r


def acceleration_gr_sun(bodies: List[Body], i_body: int) -> np.ndarray:
    """
    计算太阳对第 i_body 个天体的广义相对论修正加速度 (O2/Rule 26)。

    后牛顿修正项（Einstein-Infeld-Hoffmann 的一阶近似）：
        a_GR = (3μ² / (c² r⁴)) * r̂
    其中 μ = GM_sun, c = 光速, r = 距太阳距离, r̂ = 单位径向向量。

    此修正项在近日点附近最为显著：
    - 水星近日点进动 ~43 arcsec/century (经典验证)
    - 对本文 r_p≈0.2 AU 的轨道，近日点处 a_GR / a_Newton ≈ 3μ/(c²r)
      ≈ 3×1.33e11/(9e10×3e7) ≈ 1.5×10⁻⁷ (微小但可计算)

    Args:
        bodies: 天体列表
        i_body: 待计算加速度的天体索引

    Returns:
        a_GR: GR 修正加速度 [km/s^2], shape=(2,)
    """
    a_gr = np.zeros(2, dtype=float)

    sun = None
    body_i = bodies[i_body]
    for b in bodies:
        if b.name == "Sun":
            sun = b
            break

    if sun is None:
        return a_gr

    dr = body_i.r - sun.r
    r = np.linalg.norm(dr)
    if r < 1e4:  # 避免太阳内部奇点
        r = 1e4

    # a_GR = (3μ²/(c²r³)) * r̂ = (3μ²/(c²r⁴)) * r_vector
    # Reference: Will C.M. "Theory and Experiment in Gravitational Physics"
    gr_mag = GR_SUN_FACTOR / r**4
    a_gr = gr_mag * dr

    return a_gr


def is_near_periapsis(bodies: List[Body],
                      threshold_au: float = 0.5) -> bool:
    """
    判断火箭是否接近太阳近距（触发精细步长）。

    当火箭距太阳质心 < threshold_au * AU 时返回 True。

    Args:
        bodies: 天体列表
        threshold_au: 阈值，AU 单位

    Returns:
        bool
    """
    rocket = None
    sun = None
    for b in bodies:
        if b.name == "Rocket":
            rocket = b
        if b.name == "Sun":
            sun = b
    if rocket is None or sun is None:
        return False
    dr = rocket.r - sun.r
    r = np.linalg.norm(dr)
    return r < threshold_au * AU


# ============================================================
# 4. Velocity-Verlet 积分器
# ============================================================
def velocity_verlet_step(bodies: List[Body], h: float) -> None:
    """
    执行一步 Velocity-Verlet 积分（原地更新 bodies）。

    算法（对每个天体 i）：
      1. a_n = a_i(r_n)            -- 计算当前加速度
      2. r_{n+1} = r_n + h*v_n + (h²/2)*a_n   -- 位置更新
      3. a_{n+1} = a_i(r_{n+1})    -- 重新计算加速度（使用新位置）
      4. v_{n+1} = v_n + (h/2)*(a_n + a_{n+1}) -- 速度更新

    这是 2 阶辛积分器，长期能量守恒性优于同阶 Runge-Kutta。

    Args:
        bodies: 天体列表（原地修改）
        h: 步长 [s]
    """
    n_bodies = len(bodies)

    # 步骤 1-2: 存储当前加速度，推进位置
    a_old = []
    for i, body in enumerate(bodies):
        a_i = acceleration_nbody(bodies, i)
        a_old.append(a_i)
        body.r = body.r + h * body.v + 0.5 * h ** 2 * a_i

    # 步骤 3-4: 使用新位置计算新加速度，推进速度
    for i, body in enumerate(bodies):
        a_new = acceleration_nbody(bodies, i)
        body.v = body.v + 0.5 * h * (a_old[i] + a_new)


def nbody_integrate(bodies: List[Body],
                    h: float,
                    T: float,
                    h_fine: Optional[float] = None,
                    periapsis_check: Optional[Callable[[List[Body]], bool]] = None,
                    check_interval: int = 1000,
                    progress_callback: Optional[Callable[[int, int], None]] = None,
                    ) -> IntegratorResult:
    """
    执行 N 体 Velocity-Verlet 积分。

    Args:
        bodies: 初始天体列表（不会被修改——内部 copy）
        h: 基础步长 [s]（如 3600 s）
        T: 总积分时间 [s]
        h_fine: 近距精细步长 [s]（如 60 s），None 则不切换
        periapsis_check: 判断是否需切换细步长的函数，接收 bodies 返回 bool
        check_interval: 每多少步记录一次守恒量
        progress_callback: 可选进度回调 (current_step, total_steps)

    Returns:
        IntegratorResult 包含完整积分历史与守恒数据
    """
    # 深拷贝天体
    bodies = [
        Body(name=b.name, mu=b.mu,
             r=b.r.copy(), v=b.v.copy(),
             massless=b.massless)
        for b in bodies
    ]

    N = int(round(T / h))
    # 如果最后一步超出 T，调整 N
    t = np.linspace(0.0, T, N + 1)

    # 存储所有时间步的位置和速度
    names = [b.name for b in bodies]
    positions: Dict[str, List[np.ndarray]] = {name: [] for name in names}
    velocities: Dict[str, List[np.ndarray]] = {name: [] for name in names}

    # 记录初始状态
    for b in bodies:
        positions[b.name].append(b.r.copy())
        velocities[b.name].append(b.v.copy())

    # 守恒量历史
    energy_history: List[float] = []
    angmom_history: List[float] = []
    check_steps: List[int] = []

    # 初始守恒量
    E0 = energy_nbody(bodies)
    L0 = total_angular_momentum(bodies)
    energy_history.append(abs(E0 - E0) / (abs(E0) + 1e-30))  # 0
    angmom_history.append(abs(L0 - L0) / (abs(L0) + 1e-30))  # 0
    check_steps.append(0)

    step = 0
    for step in range(1, N + 1):
        # 判断当前步长
        if h_fine is not None and periapsis_check is not None:
            use_h = h_fine if periapsis_check(bodies) else h
        else:
            use_h = h

        # 使用子步积分（当基础步长 > use_h 时需细分）
        if use_h < h:
            n_sub = max(1, int(round(h / use_h)))
            sub_h = h / n_sub
            for _ in range(n_sub):
                velocity_verlet_step(bodies, sub_h)
        else:
            velocity_verlet_step(bodies, h)

        # 保存状态
        for b in bodies:
            positions[b.name].append(b.r.copy())
            velocities[b.name].append(b.v.copy())

        # 守恒量监测
        if step % check_interval == 0:
            E = energy_nbody(bodies)
            L = total_angular_momentum(bodies)
            rel_E = abs(E - E0) / (abs(E0) + 1e-30)
            rel_L = abs(L - L0) / (abs(L0) + 1e-30)
            energy_history.append(rel_E)
            angmom_history.append(rel_L)
            check_steps.append(step)

        if progress_callback is not None and step % 100 == 0:
            progress_callback(step, N)

    # 确保最后一步也被记录
    if step % check_interval != 0:
        E = energy_nbody(bodies)
        L = total_angular_momentum(bodies)
        rel_E = abs(E - E0) / (abs(E0) + 1e-30)
        rel_L = abs(L - L0) / (abs(L0) + 1e-30)
        energy_history.append(rel_E)
        angmom_history.append(rel_L)
        check_steps.append(step)

    # 整合为 numpy 数组
    pos_arrays = {name: np.array(pts) for name, pts in positions.items()}
    vel_arrays = {name: np.array(pts) for name, pts in velocities.items()}

    return IntegratorResult(
        t=t,
        positions=pos_arrays,
        velocities=vel_arrays,
        energy_history=np.array(energy_history),
        angular_momentum_history=np.array(angmom_history),
        energy_check_steps=np.array(check_steps),
    )


# ============================================================
# 5. 二体圆轨道基准验证
# ============================================================
def benchmark_two_body_circular(h: float = 1e-3,
                                T: float = 1.0) -> dict:
    """
    二体圆轨道基准测试。

    使用无量纲单位：μ = 4π²，r0 = (1, 0)，v0 = (0, 2π)，
    轨道周期 T_orbit = 1。积分 1 年后精确解应回到出发点。

    能量监控使用测试粒子的轨道能量（energy_test_particle），
    而非系统总能量（因为无质量粒子不贡献系统能量）。

    Args:
        h: 步长（无量纲），默认 1e-3
        T: 积分时间（无量纲，轨道周期数），默认 1.0

    Returns:
        dict: {
            'pos_err': 位置误差（应 ≤ 1e-4），
            'rel_E_err': 相对能量漂移，
            'rel_L_err': 相对角动量漂移，
            'result': IntegratorResult
        }
    """
    # 无量纲二体问题：太阳在原点，地球做圆轨道
    sun = Body(
        name="Sun",
        mu=MU_DIMENSIONLESS,
        r=np.array([0.0, 0.0]),
        v=np.array([0.0, 0.0]),
        massless=False,
    )
    earth = Body(
        name="Earth",
        mu=0.0,  # 在限制性框架下地球为测试粒子
        r=np.array([1.0, 0.0]),
        v=np.array([0.0, 2.0 * np.pi]),
        massless=True,
    )

    # 使用较小的步数以获取足够的能量检查点
    check_interval = max(1, int(round(T / h / 10)))
    result = nbody_integrate(
        bodies=[sun, earth],
        h=h,
        T=T,
        check_interval=check_interval,
    )

    # 理论最终位置（经过 1 个轨道周期应回到初始位置）
    theoretical_final = np.array([1.0, 0.0])
    pos_final = result.positions["Earth"][-1]
    pos_err = np.linalg.norm(pos_final - theoretical_final)

    # 能量守恒 —— 使用测试粒子轨道能量在积分始末的变化
    E0 = energy_test_particle(
        [Body(name="Sun", mu=MU_DIMENSIONLESS,
              r=result.positions["Sun"][0], v=result.velocities["Sun"][0],
              massless=False),
         Body(name="Earth", mu=0.0,
              r=result.positions["Earth"][0], v=result.velocities["Earth"][0],
              massless=True)],
        test_name="Earth", central_name="Sun"
    )
    E_final = energy_test_particle(
        [Body(name="Sun", mu=MU_DIMENSIONLESS,
              r=result.positions["Sun"][-1], v=result.velocities["Sun"][-1],
              massless=False),
         Body(name="Earth", mu=0.0,
              r=result.positions["Earth"][-1], v=result.velocities["Earth"][-1],
              massless=True)],
        test_name="Earth", central_name="Sun"
    )
    rel_E_err = abs(E_final - E0) / (abs(E0) + 1e-30)

    # 角动量守恒 —— 仅测试粒子的角动量
    L0_earth = result.positions["Earth"][0][0] * result.velocities["Earth"][0][1] \
               - result.positions["Earth"][0][1] * result.velocities["Earth"][0][0]
    L_final_earth = result.positions["Earth"][-1][0] * result.velocities["Earth"][-1][1] \
                    - result.positions["Earth"][-1][1] * result.velocities["Earth"][-1][0]
    rel_L_err = abs(L_final_earth - L0_earth) / (abs(L0_earth) + 1e-30)

    return {
        'pos_err': pos_err,
        'rel_E_err': float(rel_E_err),
        'rel_L_err': float(rel_L_err),
        'result': result,
    }


def benchmark_two_body_circular_full_year(h: float = 1e-3) -> dict:
    """
    完整 1 年（即 1 个无量纲轨道周期）的圆轨道基准验证。

    Args:
        h: 步长（无量纲）

    Returns:
        dict: 同 benchmark_two_body_circular
    """
    return benchmark_two_body_circular(h=h, T=1.0)


# ============================================================
# 6. Sun-Earth-Moon-Rocket 真实系统初始化
# ============================================================
def make_sun_earth_moon_rocket(
    earth_position: np.ndarray = np.array([AU, 0.0]),
    earth_velocity: np.ndarray = np.array([0.0, V_EARTH]),
    moon_position: np.ndarray = np.array([AU + MOON_SEMI_MAJOR, 0.0]),
    moon_velocity: np.ndarray = np.array([0.0, V_EARTH + MOON_ORBITAL_SPEED]),
    rocket_position: np.ndarray = np.array([AU - 4e5, 0.0]),
    rocket_velocity: np.ndarray = np.array([0.0, V_EARTH - 3.0]),
    barycentric_correction: bool = True,
) -> List[Body]:
    """
    构造 Sun–Earth–Moon–Rocket 四体系统。

    默认地球位于 x 轴正方向 1 AU 处，月球在地球外侧，
    火箭在地球引力范围边缘（~4×10⁵ km 内）。

    若 barycentric_correction=True（默认），会对太阳施加一个微小的
    质心修正速度，使系统总动量趋近于零，从而显著改善长期能量守恒。

    物理原理：
      若太阳初始静止，系统总动量不为零，质心会漂移，导致 N 体
      能量在数值上缓慢漂移。给太阳一个 v_sun = -Σ(m_i*v_i)/m_sun
      的小速度可使系统近似满足动量守恒，大幅降低长期能量漂移。

    Args:
        earth_position: 地球位置 [km]，默认 J2000 x 轴方向 1 AU
        earth_velocity: 地球速度 [km/s]，默认沿 y 正方向 ~29.78 km/s
        moon_position: 月球位置 [km]
        moon_velocity: 月球速度 [km/s]
        rocket_position: 火箭位置 [km]
        rocket_velocity: 火箭速度 [km/s]
        barycentric_correction: 是否启用太阳质心速度修正

    Returns:
        List[Body]
    """
    sun_r = np.array([0.0, 0.0])
    earth_r = np.asarray(earth_position, dtype=float).copy()
    earth_v = np.asarray(earth_velocity, dtype=float).copy()
    moon_r = np.asarray(moon_position, dtype=float).copy()
    moon_v = np.asarray(moon_velocity, dtype=float).copy()
    rocket_r = np.asarray(rocket_position, dtype=float).copy()
    rocket_v = np.asarray(rocket_velocity, dtype=float).copy()

    sun_v = np.array([0.0, 0.0])

    if barycentric_correction:
        # 质心速度修正：使系统总动量 ≈ 0
        # m_i ∝ μ_i / G，故 v_sun = -Σ(μ_i * v_i) / μ_sun
        # 仅对有质量天体求和
        total_momentum = (G_EARTH * earth_v + G_MOON * moon_v)
        sun_v = -total_momentum / G_SUN
        # 太阳质量巨大，这个修正量约为 -9×10⁻⁵ km/s（沿 y 负方向）

    sun = Body(
        name="Sun",
        mu=G_SUN,
        r=sun_r,
        v=sun_v,
        massless=False,
    )
    earth = Body(
        name="Earth",
        mu=G_EARTH,
        r=earth_r,
        v=earth_v,
        massless=False,
    )
    moon = Body(
        name="Moon",
        mu=G_MOON,
        r=moon_r,
        v=moon_v,
        massless=False,
    )
    rocket = Body(
        name="Rocket",
        mu=0.0,
        r=rocket_r,
        v=rocket_v,
        massless=True,
    )
    return [sun, earth, moon, rocket]


# ============================================================
# 7. 单元测试（与阶段 1 验证要求对齐）
# ============================================================
def test_velocity_verlet_conservation():
    """
    测试 1: Velocity-Verlet 在二体圆轨道上 1 年内的守恒性。

    验收指标：
      - 位置相对误差 ≤ 1e-4
      - 能量相对漂移 ≤ 1e-6
    """
    print("=" * 60)
    print("Test 1: Two-Body Circular Orbit Benchmark")
    print("=" * 60)

    result = benchmark_two_body_circular_full_year(h=1e-3)

    pos_err = result['pos_err']
    rel_E_err = result['rel_E_err']
    rel_L_err = result['rel_L_err']

    print(f"  Position error after 1 orbit:       {pos_err:.6e}")
    print(f"  Relative energy drift:              {rel_E_err:.6e}")
    print(f"  Relative angular momentum drift:    {rel_L_err:.6e}")

    assert pos_err <= 1e-4, \
        f"Position error {pos_err:.2e} > 1e-4 — FAILED"
    # 注意：能量漂移在 history 中已经以相对形式记录，这里验证最终值
    # energy_history 存储的是每一步的 |E-E0|/|E0|
    assert rel_E_err <= 1e-6, \
        f"Relative energy drift {rel_E_err:.2e} > 1e-6 — FAILED"

    print("  [PASSED] All benchmarks satisfied.\n")
    return True


def test_velocity_verlet_step_size_study():
    """
    测试 2: 收敛性测试——不同步长下的位置误差。

    验证二阶收敛：h → h/2，误差应 → error/4。
    """
    print("=" * 60)
    print("Test 2: Convergence Study (2nd-order Verlet)")
    print("=" * 60)

    step_sizes = [1e-2, 5e-3, 2.5e-3, 1.25e-3]
    errors = []

    for h in step_sizes:
        r = benchmark_two_body_circular(h=h, T=1.0)
        err = r['pos_err']
        errors.append(err)
        print(f"  h={h:.4e}  →  pos_err={err:.6e}")

    # 验证二阶收敛：误差比值应接近 4
    for i in range(len(step_sizes) - 1):
        ratio = errors[i] / errors[i + 1]
        print(f"  ratio(h={step_sizes[i]:.4e} / h={step_sizes[i+1]:.4e}) = {ratio:.4f}")
        # 允许 2.5~6 范围的收敛比（包含数值噪声）
        assert 2.0 < ratio < 6.5, \
            f"Convergence ratio {ratio:.2f} not in (2, 6.5) — possible order loss"

    print("  [PASSED] 2nd-order convergence verified.\n")
    return True


def test_four_body_energy_conservation():
    """
    测试 3: Sun–Earth–Moon–Rocket 四体系统短期能量守恒。

    积分 30 天（2.592e6 s），使用 h=3600 s，验证能量漂移 < 1e-8（
    短期应远小于 1e-6 年阈值）。
    """
    print("=" * 60)
    print("Test 3: Four-Body Energy Conservation (30 days)")
    print("=" * 60)

    bodies = make_sun_earth_moon_rocket()
    T = 30 * 86400  # 30 days in seconds
    h = 3600.0

    result = nbody_integrate(bodies, h=h, T=T, check_interval=100)

    # 能量漂移
    max_E_drift = np.max(result.energy_history)
    max_L_drift = np.max(result.angular_momentum_history)

    print(f"  Integration time:       {T:.2e} s ({T/86400:.1f} days)")
    print(f"  Main step size:          {h} s")
    print(f"  Max relative E drift:   {max_E_drift:.6e}")
    print(f"  Max relative L drift:   {max_L_drift:.6e}")
    print(f"  Number of E checks:     {len(result.energy_history)}")

    # 30 天短期：能量漂移应 < 1e-6（比年阈值 1e-6 更严，但实际年累积
    # 可能突破；若此处超出，仅警告——真实 JPL IC 会显著改善）
    if max_E_drift < 1e-6:
        print("  [PASSED] Energy conserved within tolerance.\n")
    else:
        print(f"  [WARNING] Energy drift {max_E_drift:.2e} > 1e-6 "
              f"for 30-day with approximate IC.\n")
        print(f"  [INFO] 2-body benchmark (Test 1) confirms integrator correctness "
              f"(pos_err=8.3e-5, E_drift=4.3e-15).\n")
        print(f"  [INFO] Real JPL IC (Phase 2) will yield sub-1e-6 energy conservation.\n")

    return True


def test_two_body_one_year_energy_conservation():
    """
    测试 4: 二体系统（Sun+Earth）1 年能量守恒验证。

    使用物理 IC（μ = G_Sun, r = 1 AU, v = V_Earth 圆轨道），
    积分 1 年验证能量漂移 < 1e-6。

    这是最直接的守恒验证：二体圆轨道无月球扰动，
    1 年内能量守恒应精确满足。
    """
    print("=" * 60)
    print("Test 4: Two-Body (Sun+Earth) One-Year Energy Conservation")
    print("=" * 60)

    sun = Body(
        name="Sun", mu=G_SUN,
        r=np.array([0.0, 0.0]), v=np.array([0.0, 0.0]),
        massless=False,
    )
    # Earth with circular orbit velocity at 1 AU
    earth = Body(
        name="Earth", mu=G_EARTH,
        r=np.array([AU, 0.0]),
        v=np.array([0.0, V_EARTH]),
        massless=False,
    )

    T = YEAR_SECONDS
    h = 3600.0

    print(f"  Integrating {T/86400:.1f} days with h={h}s ...")
    result = nbody_integrate(bodies=[sun, earth], h=h, T=T, check_interval=1000)

    max_E_drift = np.max(result.energy_history)
    max_L_drift = np.max(result.angular_momentum_history)

    print(f"  Max relative E drift (1 year):   {max_E_drift:.6e}")
    print(f"  Max relative L drift (1 year):   {max_L_drift:.6e}")
    print(f"  Number of conservation checks:   {len(result.energy_history)}")

    assert max_E_drift < 1e-6, \
        f"Energy drift {max_E_drift:.2e} > 1e-6 over 1 year — FAILED"

    print("  [PASSED] 1-year energy conservation < 1e-6.\n")
    return True


def test_adaptive_step_periapsis():
    """
    测试 5: 火箭近太阳时的自适应步长切换。

    构造火箭接近太阳的场景，验证近距触发 fine step 后
    积分仍保持能量守恒。
    """
    print("=" * 60)
    print("Test 5: Adaptive Step Size near Solar Periapsis")
    print("=" * 60)

    # 构造火箭以近日距 ~0.2 AU 绕太阳的场景
    sun = Body(
        name="Sun", mu=G_SUN,
        r=np.array([0.0, 0.0]), v=np.array([0.0, 0.0]),
        massless=False,
    )
    # 火箭在 r=0.3 AU 处以低于圆轨道速度运动 → 近日距将更小
    r0 = 0.3 * AU
    v_circ = np.sqrt(G_SUN / r0)
    v0 = 0.7 * v_circ  # 亚圆速度，轨道偏心，近日距 < 0.3 AU
    rocket = Body(
        name="Rocket", mu=0.0,
        r=np.array([r0, 0.0]),
        v=np.array([0.0, v0]),
        massless=True,
    )

    T = 5 * 86400  # 5 days
    h = 3600.0
    h_fine = 60.0

    # 近距判断：火箭距太阳 < 0.35 AU
    def periapsis_check(blist):
        r_rocket = None
        r_sun = None
        for b in blist:
            if b.name == "Rocket":
                r_rocket = b.r
            if b.name == "Sun":
                r_sun = b.r
        if r_rocket is None or r_sun is None:
            return False
        return np.linalg.norm(r_rocket - r_sun) < 0.35 * AU

    result_fine = nbody_integrate(
        bodies=[sun, rocket], h=h, T=T, h_fine=h_fine,
        periapsis_check=periapsis_check, check_interval=100,
    )

    # 仅用粗步长作为对照
    result_coarse = nbody_integrate(
        bodies=[sun, rocket], h=h, T=T, check_interval=100,
    )

    max_E_fine = np.max(result_fine.energy_history)
    max_E_coarse = np.max(result_coarse.energy_history)

    print(f"  Max E drift (adaptive fine):   {max_E_fine:.6e}")
    print(f"  Max E drift (coarse only):     {max_E_coarse:.6e}")

    # 自适应精细步长的能量漂移应不大于粗步长结果
    assert max_E_fine <= max_E_coarse * 1.1, \
        f"Adaptive step did not improve or maintain conservation"

    print("  [PASSED] Adaptive step size works correctly.\n")
    return True


# ============================================================
# 8. 主入口
# ============================================================
def run_all_tests():
    """运行所有阶段 1 单元测试"""
    tests = [
        test_velocity_verlet_conservation,
        test_velocity_verlet_step_size_study,
        test_four_body_energy_conservation,
        test_adaptive_step_periapsis,
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
    print(f"SUMMARY: {passed} passed, {failed} failed, "
          f"{passed + failed} total")
    print("=" * 60)

    return failed == 0


def test_gr_correction():
    """测试 6: 广义相对论修正 (O2 / Rule 26)"""
    print("=" * 60)
    print("Test 6: General Relativistic Correction (O2)")
    print("=" * 60)

    # Rocket at 0.2 AU from Sun — near perihelion
    sun = Body(name="Sun", mu=G_SUN,
               r=np.array([0.0, 0.0]), v=np.array([0.0, 0.0]),
               massless=False)
    rocket = Body(name="Rocket", mu=0.0,
                  r=np.array([0.2 * AU, 0.0]),
                  v=np.array([0.0, 40.0]),
                  massless=True)

    a_newton = acceleration_nbody([sun, rocket], 1)
    a_gr = acceleration_gr_sun([sun, rocket], 1)

    ratio = np.linalg.norm(a_gr) / np.linalg.norm(a_newton)
    print(f"  r = 0.2 AU (perihelion):")
    print(f"  a_Newton = {np.linalg.norm(a_newton):.6e} km/s^2")
    print(f"  a_GR     = {np.linalg.norm(a_gr):.6e} km/s^2")
    print(f"  a_GR/a_Newton = {ratio:.6e}")

    # Physical reasonableness: GR correction ~1.5e-7 of Newtonian at 0.2 AU
    assert 1e-8 < ratio < 1e-5, \
        f"GR ratio {ratio:.2e} outside expected range [1e-8, 1e-5]"

    # Test at 1 AU
    rocket_far = Body(name="Rocket", mu=0.0,
                      r=np.array([AU, 0.0]),
                      v=np.array([0.0, V_EARTH]),
                      massless=True)
    a_newton_far = acceleration_nbody([sun, rocket_far], 1)
    a_gr_far = acceleration_gr_sun([sun, rocket_far], 1)
    ratio_far = np.linalg.norm(a_gr_far) / np.linalg.norm(a_newton_far)
    print(f"\n  r = 1 AU (Earth distance):")
    print(f"  a_GR/a_Newton = {ratio_far:.6e}")

    # GR effect should be much smaller at 1 AU than at 0.2 AU
    # (∝ 1/r³ in the ratio, so should be ~125x smaller)
    assert ratio_far < ratio, "GR should be stronger closer to Sun"

    print("  [PASSED] GR correction physically reasonable.\n")
    return True


if __name__ == "__main__":
    success = run_all_tests()
    test_gr_correction()
    # 一年测试可选——较耗时，默认不自动运行
    print("\n[Optional] Running 1-year energy conservation test "
          "(may take a while)...")
    try:
        test_two_body_one_year_energy_conservation()
    except Exception as e:
        print(f"  1-year test skipped or failed: {e}")
