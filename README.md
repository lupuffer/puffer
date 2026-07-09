# 鲁振哲 (Zhenzhe Lu) — 个人代码仓库

> 📧 luzhenzhe2006@qq.com | 🏫 浙江大学管理学院 | 信息管理与信息系统  
> 🔗 https://github.com/lupuffer/puffer

---

## 📁 仓库结构

```
puffer/
├── index.html               # 个人主页（自包含单文件，双击即开）
├── resume.tex               # LaTeX 简历源码
├── resume.pdf               # 预编译简历 PDF
├── assets/                  # 静态资源
├── seekbook/                # 📚 SeekBook 二手书交易系统
├── trajectory-optimizer/    # 🚀 钱学森轨道优化项目
└── README.md
```

---

## 📚 项目一：SeekBook 二手书与知识资产流转系统

Vue 3 + Flask 全栈Web应用，十万级虚拟书籍数据支撑的校园二手书交易与知识社区平台。

- **角色**：核心开发者（团队协作）
- **技术栈**：Vue 3 · Flask · SQLAlchemy · SQLite · 通义千问 · ECharts · Vite
- **亮点**：Blueprint 微服务架构 · ISBN 双轨识别 · 知识星河社区 · 零余额线下对交
- 详见 [seekbook/](seekbook/)

## 🚀 项目二：钱学森问题扩展求解——绕日返回轨道设计

基于钱学森《星际航行概论》(2008) 第5-6章框架，AI 辅助开发的高精度N体积分器与多重打靶优化算法。

- **角色**：AI 辅助开发
- **技术栈**：Python · NumPy · Matplotlib · AstroPy · LaTeX · 遗传算法 · N体模拟
- **亮点**：自研 Velocity-Verlet 辛积分器，能量漂移 4.32×10⁻¹⁵；钱学森算例复现偏差 ≤ 0.1%
- 详见 [trajectory-optimizer/](trajectory-optimizer/)

---

## 🏠 个人主页

`index.html` — 纯 HTML/CSS/JS 单文件，双击即开。包含教育背景、研究方向、项目展示、可打印简历、获奖情况。

## 📄 简历

- **在线版**：打开个人主页 → 简历 → 打印/导出PDF
- **LaTeX 源码**：`resume.tex`，`xelatex resume.tex` 编译
- **预编译 PDF**：`resume.pdf`

---

© 2026 鲁振哲 · Zhenzhe Lu · 浙江大学管理学院
