# 钱学森问题扩展求解：火箭绕过太阳返回地球的轨道设计

> **《人工智能与数学软件》期末设计项目**  
> 基于钱学森《星际航行概论》(2008) 第5-6章框架  
> 含月球借力与发射窗口优化的绕日返回轨道设计

---

## 快速开始 (5 分钟可完全重现)

### 环境要求

| 组件 | 版本要求 |
|------|---------|
| Python | ≥ 3.9 |
| NumPy | ≥ 1.20 |
| Matplotlib | ≥ 3.5 |
| Pandas | ≥ 1.4 |
| astroquery | ≥ 0.4 (JPL Horizons 数据获取) |
| astropy | ≥ 5.0 (astroquery 依赖) |
| ffmpeg | 系统安装 (MP4 动画渲染) |
| XeLaTeX | 系统安装 (PDF 编译) |

### 一键安装与运行

```bash
# 1. 安装 Python 依赖
pip install numpy matplotlib pandas astroquery astropy

# 2. 运行所有单元测试 (验证环境)
make test

# 3. 一键生成全部交付物 (图表 + 动画 + PDF)
make all

# 4. 仅编译 report.pdf
make pdf

# 5. 清理生成文件
make clean
```

### 模块清单

| 模块 | 文件 | 功能说明 |
|------|------|---------|
| 阶段 1 | `src/nbody.py` | 高精度 N 体 Velocity-Verlet 积分器 |
| 阶段 2 | `src/horizons_verify.py` | JPL Horizons 历表对接与残差校验 |
| 阶段 3 | `src/patched_conic.py` | 钱学森拼接圆锥曲线解析算法 + 月球借力 |
| 阶段 4 | `src/trajectory_optimizer.py` | 发射窗口双层扫描优化 |
| 阶段 5 | `src/plot_results.py` | 可视化：静态图 + MP4 轨道动画 |
| R11 | `src/numerical_optimizer.py` | **多重打靶法数值优化 (新增)** |
| R15-16 | `src/end_to_end_trajectory.py` | 端到端轨迹鲁棒求解器 (3阶段自适应搜索) |
| R17 | `src/trajectory_optimizer.py` | Δv 预算口径（物理残差分解计算） |
| R22 | `src/nbody_3d.py` | 3D 扩展 + 月球倾角全年定量分析 |
| R23 | `src/differential_corrector.py` | 自研 Newton-Raphson + Lambert 求解器 |
| R24 | `src/multi_flyby.py` | Earth→Moon→Venus→Sun→Earth 多次借力 |
| R25 | `src/interactive_orbit.py` | Tkinter 交互式轨道演示 |
| R26 | `src/nbody.py` (GR) | 广义相对论后牛顿修正 |
| R27 | `src/ga_optimizer.py`, `src/parallel_computing.py` | 遗传算法 + 并行蒙特卡洛 |
| 构建 | `Makefile` | 一键构建 `make all` |
| 报告 | `report.tex` | XeLaTeX 学术报告 |

### 输出文件一览

```
figures/
  orbit_trajectory.png      # 轨道转移二维轨迹图
  energy_conservation.png   # 能量守恒对数曲线图
  dv_vs_launch_date.png     # 365天 Δv(t₀) 曲线图
  residuals.png             # 历表残差图

output/
  orbit_animation.mp4       # 轨道全景动画 (30-60s)
  horizons_verify/
    residuals_2026.csv      # 残差明细表

report.pdf                  # 最终学术报告
```

---

## 项目技术架构

```
                     ┌──────────────────────┐
                     │  report.tex (学术报告) │
                     └──────────┬───────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
  ┌──────▼──────┐  ┌───────────▼──────────┐  ┌────────▼───────┐
  │ patched_conic │  │ trajectory_optimizer │  │  plot_results  │
  │  解析轨道算法  │  │   双层扫描优化       │  │   可视化交付    │
  └──────┬──────┘  └───────────┬──────────┘  └────────┬───────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                      ┌─────────▼──────────┐
                      │     nbody.py        │
                      │  N 体 Velocity-Verlet│
                      └────────┬───────────┘
                               │
                      ┌────────▼───────────┐
                      │ horizons_verify.py  │
                      │  JPL 历表对接校验   │
                      └────────────────────┘
```

### 物理模型

- **参考系**: J2000 黄道平面投影 (2D)
- **引力模型**: Sun-Earth-Moon-Rocket 四体 (限制性)
- **积分器**: 2 阶辛积分器 Velocity-Verlet
- **步长**: 主步长 h=3600s；近距精细 h=60s
- **解析法**: 钱学森拼接圆锥曲线法 (patched conic method)

---

## 基准验证结果

### 阶段 1: N 体积分器精度

| 测试 | 指标 | 结果 | 要求 |
|------|------|------|------|
| 二体圆轨道 | 位置误差 (1年) | 8.27×10⁻⁵ | ≤ 10⁻⁴ |
| 二体圆轨道 | 能量漂移 (1年) | 4.32×10⁻¹⁵ | ≤ 10⁻⁶ |
| 收敛阶 | 误差收敛比 | 3.995~4.000 | ~4 (2阶) |
| Sun+Earth | E 漂移 (1年) | 1.35×10⁻⁸ | < 10⁻⁶ |

### 阶段 3: 钱学森算例复现

| 参数 | 程序解 | 原算例 | 偏差 |
|------|--------|--------|------|
| 半长轴 a | 0.600000 AU | 0.6 AU | 0.00% |
| 偏心率 e | 0.666667 | 0.6667 | 0.00% |
| 日心速度 v₁ | 17.195 km/s | 17.21 km/s | 0.09% |
| Δv | -12.588 km/s | -12.59 km/s | 0.02% |
| 发射速度 | 16.836 km/s | 16.84 km/s | 0.02% |
| 周期 T | 169.8 天 | 169.8 天 | 0.03% |

> 所有参数偏差 ≤ 0.1%，满足 M1 指标。

---

## 作者

Claude Code (deepseek-v4-pro) + 人工审校  
2026-06-17

## 参考文献

- 钱学森. 《星际航行概论》. 中国科学技术大学出版社, 2008.
- Vallado, D.A. *Fundamentals of Astrodynamics and Applications*. 4th Ed.
- JPL DE440 Ephemeris. https://ssd.jpl.nasa.gov/horizons/