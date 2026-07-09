const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, ExternalHyperlink, LevelFormat
} = require("docx");

// ========== Helpers ==========
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

function sectionTitle(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 300, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E5A88", space: 4 } },
    children: [new TextRun({ text, bold: true, size: 26, font: "Microsoft YaHei", color: "2E5A88" })],
  });
}

function bodyP(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.after || 60, line: 276 },
    children: [new TextRun({ text, size: 21, font: "Microsoft YaHei", ...opts })],
  });
}

function boldThenNormal(boldText, normalText) {
  return new Paragraph({
    spacing: { after: 40, line: 276 },
    children: [
      new TextRun({ text: boldText, bold: true, size: 21, font: "Microsoft YaHei" }),
      new TextRun({ text: normalText, size: 21, font: "Microsoft YaHei" }),
    ],
  });
}

function bulletItem(text, ref = "bullets", level = 0) {
  return new Paragraph({
    numbering: { reference: ref, level },
    spacing: { after: 30, line: 264 },
    children: [new TextRun({ text, size: 20, font: "Microsoft YaHei" })],
  });
}

function bulletItemBold(boldPart, normalPart, ref = "bullets", level = 0) {
  return new Paragraph({
    numbering: { reference: ref, level },
    spacing: { after: 30, line: 264 },
    children: [
      new TextRun({ text: boldPart, bold: true, size: 20, font: "Microsoft YaHei" }),
      new TextRun({ text: normalPart, size: 20, font: "Microsoft YaHei" }),
    ],
  });
}

// ========== Document ==========
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Microsoft YaHei", size: 21 } },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Microsoft YaHei", color: "1A3A5C" },
        paragraph: { spacing: { before: 0, after: 120 }, alignment: AlignmentType.CENTER, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Microsoft YaHei", color: "2E5A88" },
        paragraph: { spacing: { before: 280, after: 100 }, outlineLevel: 1 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 600, hanging: 300 } } },
        }],
      },
      {
        reference: "bullets2",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "◦",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 900, hanging: 300 } } },
        }],
      },
    ],
  },
  sections: [
    // ========== HEADER ==========
    {
      properties: {
        page: {
          size: { width: 11906, height: 16838 }, // A4
          margin: { top: 1200, right: 1200, bottom: 1200, left: 1300 },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              alignment: AlignmentType.RIGHT,
              border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 6 } },
              children: [
                new TextRun({ text: "个人简历  |  Resume", size: 16, font: "Microsoft YaHei", color: "999999", italics: true }),
              ],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              border: { top: { style: BorderStyle.SINGLE, size: 2, color: "DDDDDD", space: 4 } },
              children: [
                new TextRun({ text: "Page ", size: 16, font: "Microsoft YaHei", color: "999999" }),
                new TextRun({ children: [PageNumber.CURRENT], size: 16, font: "Microsoft YaHei", color: "999999" }),
              ],
            }),
          ],
        }),
      },
      children: [
        // ===== NAME + CONTACT HEADER =====
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun({ text: "鲁振哲", bold: true, size: 44, font: "Microsoft YaHei" })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 60 },
          children: [new TextRun({ text: "Zhenzhe Lu", size: 22, font: "Microsoft YaHei", color: "555555", italics: true })],
        }),

        // Contact info line
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 40 },
          children: [
            new TextRun({ text: "📧 luzhenzhe2006@qq.com", size: 18, font: "Microsoft YaHei", color: "555555" }),
            new TextRun({ text: "  |  ", size: 18, font: "Microsoft YaHei", color: "CCCCCC" }),
            new TextRun({ text: "📱 131 9968 3838", size: 18, font: "Microsoft YaHei", color: "555555" }),
            new TextRun({ text: "  |  ", size: 18, font: "Microsoft YaHei", color: "CCCCCC" }),
            new TextRun({ text: "📍 浙江·杭州", size: 18, font: "Microsoft YaHei", color: "555555" }),
          ],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 60 },
          children: [
            new TextRun({ text: "🔗 ", size: 18, font: "Microsoft YaHei" }),
            new ExternalHyperlink({
              children: [new TextRun({ text: "https://gitee.com/lu-zhenzhe/personal", style: "Hyperlink", size: 18, font: "Microsoft YaHei" })],
              link: "https://gitee.com/lu-zhenzhe/personal",
            }),
          ],
        }),

        // ===== Divider =====
        new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: "2E5A88", space: 1 } },
          spacing: { after: 200 },
          children: [],
        }),

        // ========== 基本信息 ==========
        sectionTitle("基本信息"),
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [2256, 2257, 2256, 2257],
          rows: [
            new TableRow({
              children: [
                new TableCell({ borders, width: { size: 2256, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "学校", bold: true, size: 20, font: "Microsoft YaHei", color: "2E5A88" })] })] }),
                new TableCell({ borders, width: { size: 2257, type: WidthType.DXA }, margins: cellMargins,
                  children: [new Paragraph({ children: [new TextRun({ text: "浙江大学管理学院", size: 20, font: "Microsoft YaHei" })] })] }),
                new TableCell({ borders, width: { size: 2256, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "学历", bold: true, size: 20, font: "Microsoft YaHei", color: "2E5A88" })] })] }),
                new TableCell({ borders, width: { size: 2257, type: WidthType.DXA }, margins: cellMargins,
                  children: [new Paragraph({ children: [new TextRun({ text: "本科在读", size: 20, font: "Microsoft YaHei" })] })] }),
              ],
            }),
            new TableRow({
              children: [
                new TableCell({ borders, width: { size: 2256, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "专业", bold: true, size: 20, font: "Microsoft YaHei", color: "2E5A88" })] })] }),
                new TableCell({ borders, width: { size: 2257, type: WidthType.DXA }, margins: cellMargins,
                  children: [new Paragraph({ children: [new TextRun({ text: "信息管理与信息系统", size: 20, font: "Microsoft YaHei" })] })] }),
                new TableCell({ borders, width: { size: 2256, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "籍贯", bold: true, size: 20, font: "Microsoft YaHei", color: "2E5A88" })] })] }),
                new TableCell({ borders, width: { size: 2257, type: WidthType.DXA }, margins: cellMargins,
                  children: [new Paragraph({ children: [new TextRun({ text: "黑龙江省齐齐哈尔市", size: 20, font: "Microsoft YaHei" })] })] }),
              ],
            }),
            new TableRow({
              children: [
                new TableCell({ borders, width: { size: 2256, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "入学", bold: true, size: 20, font: "Microsoft YaHei", color: "2E5A88" })] })] }),
                new TableCell({ borders, width: { size: 2257, type: WidthType.DXA }, margins: cellMargins,
                  children: [new Paragraph({ children: [new TextRun({ text: "2024年9月", size: 20, font: "Microsoft YaHei" })] })] }),
                new TableCell({ borders, width: { size: 2256, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "毕业", bold: true, size: 20, font: "Microsoft YaHei", color: "2E5A88" })] })] }),
                new TableCell({ borders, width: { size: 2257, type: WidthType.DXA }, margins: cellMargins,
                  children: [new Paragraph({ children: [new TextRun({ text: "2028年6月", size: 20, font: "Microsoft YaHei" })] })] }),
              ],
            }),
          ],
        }),

        // ========== 教育背景 ==========
        sectionTitle("教育背景"),
        boldThenNormal("浙江大学（Zhejiang University）", "  |  2024.09 - 至今"),
        bodyP("管理学院 · 信息管理与信息系统 · 本科在读", { color: "555555" }),
        bodyP("主修课程：数据结构、数据库系统、运筹学、数据分析、管理信息系统、会计学、经济学等", { size: 20, color: "666666", after: 120 }),

        boldThenNormal("龙江县第一中学", "  |  2021.09 - 2024.06"),
        bodyP("理科高中 · 培养了扎实的数学和逻辑思维能力", { size: 20, color: "666666" }),

        // ========== 项目经验 ==========
        sectionTitle("项目经验"),

        // Project 1
        bodyP("🚀 钱学森问题扩展求解：绕日返回轨道设计  |  2026.06  |  独立完成", { bold: true, size: 22 }),
        bodyP("基于钱学森《星际航行概论》框架，开发高精度N体积分器与多重打靶优化算法，实现包含月球借力与发射窗口优化的绕日返回轨道设计。", { size: 20, color: "444444", after: 20, font: "Microsoft YaHei" }),
        new Paragraph({
          spacing: { after: 40 },
          children: [
            new TextRun({ text: "技术栈：", bold: true, size: 19, font: "Microsoft YaHei", color: "2E5A88" }),
            new TextRun({ text: "Python, NumPy, Matplotlib, AstroPy, LaTeX, 遗传算法, N体模拟", size: 19, font: "Microsoft YaHei", color: "666666" }),
          ],
        }),
        bulletItem("自研 Velocity-Verlet 辛积分器，能量漂移低至 4.32×10⁻¹⁵（1年仿真）"),
        bulletItem("复现钱学森拼接圆锥曲线算例，所有参数偏差 ≤ 0.1%"),
        bulletItem("实现遗传算法 + 并行蒙特卡洛全局优化框架"),
        bulletItem("对接 JPL Horizons 真实历表进行残差校验，生成完整学术报告（LaTeX）与轨道动画（MP4）"),

        new Paragraph({ spacing: { after: 160 }, children: [] }),

        // Project 2
        bodyP("📚 SeekBook 二手书与知识资产流转系统  |  2026.05  |  主要开发者", { bold: true, size: 22 }),
        bodyP("基于 Vue 3 + Flask 的全栈Web应用，构建包含十万级虚拟书籍数据的二手书交易与知识社区平台，集成ISBN智能识别与课程表知识图谱功能。", { size: 20, color: "444444", after: 20 }),
        new Paragraph({
          spacing: { after: 40 },
          children: [
            new TextRun({ text: "技术栈：", bold: true, size: 19, font: "Microsoft YaHei", color: "2E5A88" }),
            new TextRun({ text: "Vue 3, Flask, SQLAlchemy, SQLite, 通义千问 Qwen-VL, ECharts, Vite", size: 19, font: "Microsoft YaHei", color: "666666" }),
          ],
        }),
        bulletItem("设计并实现 Blueprint 微服务工厂架构，单文件严格 ≤ 200行"),
        bulletItem("开发 ISBN 双轨智能识别：通义千问 Qwen-VL 云端OCR + 文件名后门"),
        bulletItem("构建知识星河社区模块（笔记发布、模糊搜索关联、评论互动）"),
        bulletItem("实现课表 JSON 导入 → 智慧清单生成 → ECharts 知识星图可视化"),
        bulletItem("线下对交交易模式：零余额系统，见面信息 SQLite 强持久化"),

        // ========== 研究方向 ==========
        sectionTitle("研究方向"),
        bulletItemBold("数据分析：", "关注统计学习、机器学习在商业决策中的应用，探索数据驱动的管理优化方法"),
        bulletItemBold("运筹优化：", "研究数学规划、优化算法，应用于供应链管理、资源分配等实际问题"),
        bulletItemBold("数学建模：", "具备扎实的数学基础，致力于跨学科的建模挑战和实际问题求解"),

        // ========== 获奖情况 ==========
        sectionTitle("获奖情况"),
        bulletItem("全国大学生数学竞赛（非数学类B类）—— 浙江省一等奖"),
        bulletItem("微积分竞赛 —— 浙江省三等奖"),
        bulletItem("浙江大学丹青学园团总支篮球赛 —— 团体第一名"),
        bulletItem("CET-4 / CET-6 英语等级测试已通过"),

        // ========== 学生工作 ==========
        sectionTitle("学生工作"),
        boldThenNormal("管理学院学业指导中心", "  |  干事  |  2024.09 - 至今"),
        bodyP("参与管理学院学业指导中心的日常运营与活动组织工作，协助开展学业帮扶、经验分享等活动。", { size: 20, color: "555555" }),

        // ========== 技能 ==========
        sectionTitle("技能"),
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [2256, 6770],
          rows: [
            new TableRow({
              children: [
                new TableCell({ borders, width: { size: 2256, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "编程语言", bold: true, size: 19, font: "Microsoft YaHei", color: "2E5A88" })] })] }),
                new TableCell({ borders, width: { size: 6770, type: WidthType.DXA }, margins: cellMargins,
                  children: [new Paragraph({ children: [new TextRun({ text: "Python, SQL, JavaScript, HTML/CSS", size: 19, font: "Microsoft YaHei" })] })] }),
              ],
            }),
            new TableRow({
              children: [
                new TableCell({ borders, width: { size: 2256, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "框架与工具", bold: true, size: 19, font: "Microsoft YaHei", color: "2E5A88" })] })] }),
                new TableCell({ borders, width: { size: 6770, type: WidthType.DXA }, margins: cellMargins,
                  children: [new Paragraph({ children: [new TextRun({ text: "Vue 3, Flask, Vite, Git, LaTeX", size: 19, font: "Microsoft YaHei" })] })] }),
              ],
            }),
            new TableRow({
              children: [
                new TableCell({ borders, width: { size: 2256, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "数据分析", bold: true, size: 19, font: "Microsoft YaHei", color: "2E5A88" })] })] }),
                new TableCell({ borders, width: { size: 6770, type: WidthType.DXA }, margins: cellMargins,
                  children: [new Paragraph({ children: [new TextRun({ text: "NumPy, Pandas, Matplotlib", size: 19, font: "Microsoft YaHei" })] })] }),
              ],
            }),
            new TableRow({
              children: [
                new TableCell({ borders, width: { size: 2256, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "语言能力", bold: true, size: 19, font: "Microsoft YaHei", color: "2E5A88" })] })] }),
                new TableCell({ borders, width: { size: 6770, type: WidthType.DXA }, margins: cellMargins,
                  children: [new Paragraph({ children: [new TextRun({ text: "CET-4 / CET-6, 普通话", size: 19, font: "Microsoft YaHei" })] })] }),
              ],
            }),
          ],
        }),

        // ========== 自我评价 ==========
        sectionTitle("自我评价"),
        bodyP("本科在读，主修信息管理与信息系统专业。关注数据分析、运筹优化与数学建模方向，具备扎实的数学基础和逻辑思维能力。熟悉 Python 科学计算与 Vue 全栈开发，具备独立完成复杂项目的能力。善于沟通协作，乐于探索新技术，致力于将数据驱动方法应用于实际管理问题。", { size: 20, color: "444444", after: 60 }),
        new Paragraph({
          spacing: { before: 80, after: 40 },
          children: [
            new TextRun({ text: "📂 所有项目源码均托管于：", size: 19, font: "Microsoft YaHei", color: "555555" }),
            new ExternalHyperlink({
              children: [new TextRun({ text: "https://gitee.com/lu-zhenzhe/personal", style: "Hyperlink", size: 19, font: "Microsoft YaHei" })],
              link: "https://gitee.com/lu-zhenzhe/personal",
            }),
          ],
        }),
      ],
    },
  ],
});

// ========== Save ==========
const outputPath = "d:/pufferzz/3240106033/鲁振哲_个人简历_优化版.docx";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer);
  console.log("Resume saved to:", outputPath);
});
