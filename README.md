# 鲁振哲 (Zhenzhe Lu) — 个人代码仓库

> 📧 luzhenzhe2006@qq.com | 🏫 浙江大学管理学院 | 信息管理与信息系统  
> 🔗 仓库地址：https://github.com/lupuffer/puffer

---

## 📁 仓库结构

| 目录 | 内容 | 说明 |
|------|------|------|
| `3240106033/` | 个人主页 + 个人简历 | Vue 3 构建的响应式个人主页，含简历文档 |
| `FinalProject/` | 钱学森问题扩展求解 | 绕日返回轨道设计，Python科学计算项目 |
| `group2-master/` | SeekBook 二手书系统 | Vue 3 + Flask 全栈Web应用 |

---

## 🚀 项目一：钱学森问题扩展求解——绕日返回轨道设计

基于钱学森《星际航行概论》(2008) 第5-6章框架，开发高精度N体积分器与多重打靶优化算法。

### 技术亮点
- **N体模拟**：自研 Velocity-Verlet 辛积分器，能量漂移低至 4.32×10⁻¹⁵
- **钱学森算例复现**：拼接圆锥曲线法，所有参数偏差 ≤ 0.1%
- **全局优化**：遗传算法 + 并行蒙特卡洛框架
- **数据校验**：对接 JPL Horizons 真实历表
- **技术栈**：Python, NumPy, Matplotlib, AstroPy, LaTeX

详见 [FinalProject/README.md](FinalProject/README.md)

---

## 📚 项目二：SeekBook 二手书与知识资产流转系统

基于 Vue 3 + Flask 的全栈Web应用，十万级虚拟书籍数据支撑的校园二手书交易与知识社区平台。

### 功能特色
- **ISBN 双轨识别**：通义千问 Qwen-VL 云端OCR + 文件名后门
- **知识星河社区**：笔记发布、模糊搜索关联、评论互动
- **智慧清单**：课表 JSON 导入 → 知识星图 ECharts 可视化
- **线下对交**：零余额系统，见面信息 SQLite 强持久化
- **微服务架构**：Blueprint 工厂模式，单文件 ≤ 200行
- **技术栈**：Vue 3, Flask, SQLAlchemy, SQLite, ECharts, Vite

详见 [group2-master/README.md](group2-master/README.md)

---

## 🏠 个人主页

Vue 3 + Vite 构建的响应式个人主页，包含：
- 个人基本信息与教育背景
- 研究方向与学术兴趣
- **项目经验展示**（含上述两个项目）
- 获奖情况
- 阅读书单

### 本地运行
```bash
cd 3240106033/src
npm install
npm run dev
```

### 构建部署
```bash
cd 3240106033/src
npm run build
# 静态文件输出至 dist/ 目录
```

---

## 📄 个人简历

简历文件位于 `3240106033/` 目录：
- **鲁振哲_个人简历_优化版.docx** — 含项目经验的最新简历

---

## 📬 联系方式

- 📧 邮箱：luzhenzhe2006@qq.com
- 📱 电话：131 9968 3838
- 📍 地址：浙江省杭州市浙江大学紫金港校区

---

© 2026 鲁振哲 | Powered by Vue 3 + Vite
