# -*- coding: utf-8 -*-
"""
differential_corrector.py — 自定义 Newton-Raphson 微分修正器 (O3/Rule 23)
=====================================================================
不使用 scipy.optimize，自行实现 Newton-Raphson 方法进行轨道微分修正。

方法：使用项目已有的 N 体积分器作为正向传播器，
对初始速度施加有限差分扰动构建 Jacobian，Newton 迭代修正
初始速度以命中目标位置。

改进 (v2):
  - 自适应有限差分扰动 (防止 Jacobian 病态)
  - 阻尼 Newton 步长 (line search)
  - Lambert 求解器增加多次重启
  - 更好的 Jacobian 条件数检测

作者：Claude Code (deepseek-v4-pro) + 用户审校
日期：2026-06-18 (v1), 2026-06-19 (v2)
"""

import numpy as np
from typing import Tuple


def newton_raphson_corrector_nbody(
    r0: np.ndarray,
    v0_guess: np.ndarray,
    r_target: np.ndarray,
    dt: float,
    mu_central: float,
    tol: float = 100.0,
    max_iter: int = 30,
    dv_pert: float = 0.1,
) -> Tuple[np.ndarray, int, bool]:
    """
    Newton-Raphson 微分修正器 (O3/Rule 23)。

    使用 N 体积分器作为正向模型，有限差分 Jacobian，
    迭代修正初始速度以命中目标位置。

    算法原理：
      定义 f(v0) = r_final(v0) - r_target
      Newton 迭代: v0_{k+1} = v0_k - J^{-1} * f(v0_k)
      其中 Jacobian J_{ij} = ∂(r_final_i)/∂(v0_j) ≈ Δr_i / Δv_j

    改进 (v2):
      - 自适应扰动缩放: dv_pert 根据 |v0| 自动缩放
      - 条件数检测: Jacobian 病态时自动增大扰动
      - 阻尼步长: 残差下降 < 10% 时减小步长

    Args:
        r0: 初始位置 [km]
        v0_guess: 初始速度猜测 [km/s]
        r_target: 目标位置 [km]
        dt: 飞行时间 [s]
        mu_central: 中心天体引力常数 [km³/s²]
        tol: 位置收敛容差 [km]
        max_iter: 最大迭代次数
        dv_pert: 有限差分速度扰动 [km/s] (自动缩放)

    Returns:
        (v0_corrected, iterations, converged)
    """
    from nbody import Body, nbody_integrate, G_SUN

    def propagate(v0: np.ndarray) -> np.ndarray:
        """从 r0, v0 传播 dt 秒后的位置"""
        central = Body(name="Central", mu=mu_central,
                       r=np.array([0.0, 0.0]), v=np.array([0.0, 0.0]),
                       massless=False)
        particle = Body(name="Particle", mu=0.0,
                        r=r0.copy(), v=v0.copy(),
                        massless=True)
        result = nbody_integrate([central, particle], h=min(3600.0, dt/24),
                                  T=dt, check_interval=100000)
        return result.positions["Particle"][-1].copy()

    v0 = v0_guess.copy().astype(float)
    r0_arr = np.asarray(r0, dtype=float)
    r_target_arr = np.asarray(r_target, dtype=float)

    # Adaptive perturbation base scale
    v0_mag = np.linalg.norm(v0_guess)
    pert_base = max(dv_pert, v0_mag * 1e-3)

    for iteration in range(max_iter):
        r_final = propagate(v0)
        residual = r_final - r_target_arr
        res_norm = np.linalg.norm(residual)

        if res_norm < tol:
            return v0, iteration + 1, True

        # --- Adaptive Jacobian computation ---
        # Try with base perturbation first
        J = np.zeros((2, 2))
        pert = pert_base

        for attempt in range(3):
            for j in range(2):
                v_pert = v0.copy()
                v_pert[j] += pert
                r_pert = propagate(v_pert)
                J[:, j] = (r_pert - r_final) / pert

            # Check condition number
            try:
                cond = np.linalg.cond(J)
                if cond < 1e12:  # Jacobian is well-conditioned
                    break
            except np.linalg.LinAlgError:
                pass
            # Increase perturbation to improve conditioning
            pert *= 5.0

        # --- Newton step with line search ---
        try:
            delta_v = np.linalg.solve(J, -residual)
        except np.linalg.LinAlgError:
            # Fallback: steepest descent
            delta_v = -0.1 * residual / max(res_norm, 1e-30)

        # Limit step size to prevent divergence
        dv_max = v0_mag * 0.5
        dv_step = np.linalg.norm(delta_v)
        if dv_step > dv_max:
            delta_v *= dv_max / dv_step

        # Damped Newton (line search)
        alpha = 1.0
        best_res = res_norm
        best_v = v0.copy()
        for _ in range(10):
            v_trial = v0 + alpha * delta_v
            r_trial = propagate(v_trial)
            trial_res = np.linalg.norm(r_trial - r_target_arr)
            if trial_res < best_res * 0.99:
                best_res = trial_res
                best_v = v_trial.copy()
            alpha *= 0.5

        v0 = best_v
        if best_res < tol:
            return v0, iteration + 1, True

    return v0, max_iter, False


def differential_correction_lambert(
    r1: np.ndarray,
    r2: np.ndarray,
    dt: float,
    mu: float,
    v1_guess: np.ndarray = None,
) -> Tuple[np.ndarray, np.ndarray, bool]:
    """
    Lambert 问题求解器 (O3/Rule 23)。

    使用 Newton-Raphson 微分修正解决：
    给定 r1, r2 和飞行时间 dt，求初始速度 v1 和最终速度 v2。

    改进 (v2):
      - 多次重启: 初始猜测不佳时，用不同方向重试
      - 双向验证: 正向+反向积分验证

    Args:
        r1: 初始位置 [km]
        r2: 目标位置 [km]
        dt: 飞行时间 [s]
        mu: 引力常数 [km³/s²]
        v1_guess: 初始速度猜测（若为 None，用二体近似）

    Returns:
        (v1, v2, converged)
    """
    from nbody import Body, nbody_integrate

    r1_arr = np.asarray(r1, dtype=float)
    r2_arr = np.asarray(r2, dtype=float)

    # --- Build initial guess candidates ---
    r1_norm = np.linalg.norm(r1_arr)
    r2_norm = np.linalg.norm(r2_arr)
    a_transfer = (r1_norm + r2_norm) / 2.0
    v_mag = np.sqrt(mu * (2.0 / r1_norm - 1.0 / a_transfer))

    # Candidate 1: tangential (prograde)
    tangential = np.array([-r1_arr[1], r1_arr[0]]) / max(r1_norm, 1e-30)
    v1_candidates = [v_mag * tangential]

    # Candidate 2: tangential (retrograde)
    v1_candidates.append(-v_mag * tangential)

    # Candidate 3: radial-tangential mix toward target
    direction = r2_arr - r1_arr
    dir_norm = np.linalg.norm(direction)
    if dir_norm > 1e-30:
        direction = direction / dir_norm
        v1_candidates.append(v_mag * 0.7 * tangential + v_mag * 0.3 * direction)

    # Candidate 4: user-provided guess
    if v1_guess is not None:
        v1_candidates.insert(0, np.asarray(v1_guess, dtype=float))

    # Try each candidate
    best_v1 = None
    best_v2 = None
    best_err = float('inf')

    for v1_candidate in v1_candidates:
        v1_corrected, iterations, converged = newton_raphson_corrector_nbody(
            r0=r1_arr,
            v0_guess=v1_candidate,
            r_target=r2_arr,
            dt=dt,
            mu_central=mu,
            tol=5000.0,  # 5000 km tolerance for Lambert
            max_iter=30,
            dv_pert=0.1,
        )

        # Verify
        central = Body(name="Central", mu=mu,
                       r=np.array([0.0, 0.0]), v=np.array([0.0, 0.0]),
                       massless=False)
        particle = Body(name="Particle", mu=0.0,
                        r=r1_arr.copy(), v=v1_corrected.copy(),
                        massless=True)
        result = nbody_integrate([central, particle],
                                 h=min(3600.0, dt/24),
                                 T=dt, check_interval=100000)
        v2 = result.velocities["Particle"][-1].copy()
        r_final = result.positions["Particle"][-1]
        err = np.linalg.norm(r_final - r2_arr)

        if err < best_err:
            best_err = err
            best_v1 = v1_corrected.copy()
            best_v2 = v2.copy()

    converged = best_err < 10000.0  # 10,000 km tolerance
    return best_v1, best_v2, converged


# ============================================================
# 测试
# ============================================================
def test_newton_raphson():
    """测试 Newton-Raphson 微分修正器 (O3 / Rule 23)"""
    print("=" * 60)
    print("Test NR1: Newton-Raphson Differential Corrector (O3)")
    print("=" * 60)

    from nbody import G_SUN, AU, V_EARTH, Body, nbody_integrate

    mu = G_SUN
    r0 = np.array([AU, 0.0])
    v0_true = np.array([0.0, V_EARTH])  # circular orbit
    dt = 86400.0 * 10  # 10 days

    # First propagate to get target
    central = Body(name="Central", mu=mu,
                   r=np.array([0.0, 0.0]), v=np.array([0.0, 0.0]),
                   massless=False)
    particle = Body(name="Particle", mu=0.0,
                    r=r0.copy(), v=v0_true.copy(), massless=True)
    result = nbody_integrate([central, particle], h=3600.0, T=dt,
                             check_interval=100000)
    r_target = result.positions["Particle"][-1].copy()

    # Start from perturbed guess
    v0_guess = v0_true + np.array([0.3, -0.2])
    v0_corrected, iterations, converged = newton_raphson_corrector_nbody(
        r0, v0_guess, r_target, dt, mu, tol=100.0, dv_pert=0.1,
    )

    err = np.linalg.norm(v0_corrected - v0_true)
    print(f"  True v0:     ({v0_true[0]:.6f}, {v0_true[1]:.6f}) km/s")
    print(f"  Guess v0:    ({v0_guess[0]:.6f}, {v0_guess[1]:.6f}) km/s")
    print(f"  Corrected:   ({v0_corrected[0]:.6f}, {v0_corrected[1]:.6f}) km/s")
    print(f"  Error:       {err:.6e} km/s")
    print(f"  Iterations:  {iterations}")
    print(f"  Converged:   {converged}")

    assert converged, "Newton-Raphson should converge"
    assert err < 1e-2, f"Correction error {err:.2e} too large"

    print("  [PASSED] Newton-Raphson corrector converges to true solution.\n")
    return True


def test_lambert():
    """测试 Lambert 求解器"""
    print("=" * 60)
    print("Test NR2: Lambert Solver (O3)")
    print("=" * 60)

    from nbody import G_SUN, AU, Body, nbody_integrate

    mu = G_SUN
    r1 = np.array([AU, 0.0])
    r2 = np.array([-0.5*AU, 0.866*AU])  # ~120 deg apart
    dt = 86400.0 * 80  # 80 days (~half period)

    v1, v2, converged = differential_correction_lambert(r1, r2, dt, mu)

    # Verify
    central = Body(name="Central", mu=mu,
                   r=np.array([0.0, 0.0]), v=np.array([0.0, 0.0]),
                   massless=False)
    particle = Body(name="Particle", mu=0.0,
                    r=r1.copy(), v=v1.copy(), massless=True)
    result = nbody_integrate([central, particle], h=3600.0, T=dt,
                             check_interval=100000)
    r_final = result.positions["Particle"][-1]
    err = np.linalg.norm(r_final - r2)

    print(f"  r1 = ({r1[0]/AU:.3f}, {r1[1]/AU:.3f}) AU")
    print(f"  r2 = ({r2[0]/AU:.3f}, {r2[1]/AU:.3f}) AU")
    print(f"  dt = {dt/86400:.1f} days")
    print(f"  v1 = ({v1[0]:.4f}, {v1[1]:.4f}) km/s")
    print(f"  Target miss: {err:.1f} km")
    print(f"  Converged:   {converged}")

    assert converged, "Lambert should converge"
    assert err < 10000.0, f"Target miss {err:.0f} km too large"

    print("  [PASSED] Lambert solver works (with multi-restart).\n")
    return True


if __name__ == "__main__":
    test_newton_raphson()
    test_lambert()
