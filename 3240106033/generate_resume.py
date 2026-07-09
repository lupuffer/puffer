#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于简历模板生成个人简历 - 精确替换模板中的占位文本
完全仿照模板布局，保留所有图片和设计元素
"""

import json
import os
import sys
import zipfile
import re
from io import BytesIO

# ========== 数据 ==========
INFO_PATH = os.path.join(os.path.dirname(__file__), 'src', 'public', 'info.json')
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '简历模板_copy.docx')

with open(INFO_PATH, 'r', encoding='utf-8') as f:
    info = json.load(f)

# ========== 读取模板 ==========
with zipfile.ZipFile(TEMPLATE_PATH, 'r') as z:
    template_files = {}
    for item in z.namelist():
        template_files[item] = z.read(item)

document_xml = template_files['word/document.xml'].decode('utf-8')

# ========== 定义精确替换 ==========
def replace_in_wt(xml, old_text, new_text):
    """在w:t标签内精确替换文本"""
    pattern = re.compile(r'(<w:t[^>]*>)' + re.escape(old_text) + r'(</w:t>)')
    count = len(pattern.findall(xml))
    if count > 0:
        xml = pattern.sub(lambda m: m.group(1) + new_text + m.group(2), xml)
        print(f'  OK 替换[{count}处]: "{old_text}" -> "{new_text}"')
    else:
        print(f'  NO 未找到: "{old_text}"')
    return xml

# ===== 基本信息区（左侧文本框） =====
# 姓名：林晓云 -> 鲁振哲
document_xml = replace_in_wt(document_xml, '林晓云', '鲁振哲')

# 民族：：汉 -> ：汉族
document_xml = replace_in_wt(document_xml, '：汉', '：汉族')

# 电话：：13500135000 -> ：131 9968 3838
document_xml = replace_in_wt(document_xml, '：13500135000', '：131 9968 3838')

# 邮箱：邮    箱：service@500d.me -> 邮    箱：luzhenzhe2006@qq.com
document_xml = replace_in_wt(document_xml, '邮    箱：service@500d.me', '邮    箱：luzhenzhe2006@qq.com')

# 住址：住    址：广东省广州市海珠区 -> 住    址：浙江省杭州市浙江大学紫金港校区
document_xml = replace_in_wt(document_xml, '住    址：广东省广州市海珠区', '住    址：浙江省杭州市浙江大学紫金港校区')

# ===== 个人信息区（右侧文本框） =====
# 出生年月：出生年月：1996.05 -> 出生年月：2006年
document_xml = replace_in_wt(document_xml, '出生年月：1996.05', '出生年月：2006年')

# 身高：身    高：177cm -> 身    高：178cm
document_xml = replace_in_wt(document_xml, '身    高：177cm', '身    高：178cm')

# 政治面貌：政治面貌：中共党员 -> 政治面貌：共青团员
document_xml = replace_in_wt(document_xml, '政治面貌：中共党员', '政治面貌：共青团员')

# 毕业院校 -> 就读院校
document_xml = replace_in_wt(document_xml, '毕业院校', '就读院校')

# 广州 -> 浙江（在"广州"+"科技大学"上下文中）
# 先替换"科技大学"（带空格版本，右侧文本框）-> "大学管理学院"
document_xml = replace_in_wt(document_xml, '科技大学         ', '大学管理学院         ')
# 再替换"科技大学"（不带空格版本，左侧文本框）-> "大学管理学院"
document_xml = replace_in_wt(document_xml, '科技大学', '大学管理学院')
# 再替换"广州信息科技有限公司"（带空格版本，在第二段实习中）
document_xml = replace_in_wt(document_xml, '  广州信息科技有限公司      ', '  浙江大学                ')
document_xml = replace_in_wt(document_xml, '广州信息科技有限公司       ', '浙江大学                ')
# 再替换"广州" -> "浙江"
document_xml = replace_in_wt(document_xml, '广州', '浙江')

# 学历：：本科 -> ：本科在读
document_xml = replace_in_wt(document_xml, '：本科', '：本科在读')

# ===== 教育背景 =====
document_xml = replace_in_wt(document_xml, '2005.07-2009.06         ', '2024.09-至今            ')
document_xml = replace_in_wt(document_xml, '市场营销（本科）', '信息管理与信息系统（本科）')
document_xml = replace_in_wt(document_xml, '管理学、微观经济学、宏观经济学、管理信息系统、统计学、会计学、财务管理、市场营销、经济法、消费者行为学、国际市场营销', 
    '数据结构、数据库系统、运筹学、数据分析、管理信息系统、统计学、会计学、经济学')

# ===== 实习经历 -> 学生工作 =====
document_xml = replace_in_wt(document_xml, '实习经历', '学生工作')
document_xml = replace_in_wt(document_xml, '2009.03-2011.06          ', '2024.09-至今            ')
document_xml = replace_in_wt(document_xml, '广州五百丁信息科技有限公司          校园大使主席 ', '管理学院学业指导中心          干事 ')

# ===== 技能证书 -> 获奖情况 =====
document_xml = replace_in_wt(document_xml, '技能证书', '获奖情况')

# ===== 校园经历 -> 研究方向 =====
document_xml = replace_in_wt(document_xml, '校园经历', '研究方向')

# ===== 自我评价 =====
document_xml = replace_in_wt(document_xml, '自我评价', '自我评价')

# ===== 学生工作详细内容 =====
old_text = '目标带领自己的团队，辅助五百丁公司完成在各高校的\u201c伏龙计划\u201d，向全球顶尖的'
new_text = '参与管理学院学业指导中心的日常运营与活动组织工作，协助开展学业帮扶、'
document_xml = replace_in_wt(document_xml, old_text, new_text)

document_xml = replace_in_wt(document_xml, 'AXA', '')
document_xml = replace_in_wt(document_xml, '金融公司推送实习生资源。', '经验分享等活动。')

old_text2 = '整体运营前期开展了相关的线上线下宣传活动，中期为进行咨询的人员提供讲解。后期进行了项目的维护阶段，保证了整个项目的完整性。'
new_text2 = '协助整理学业指导资料，为学院同学提供学习支持与服务。'
document_xml = replace_in_wt(document_xml, old_text2, new_text2)

# ===== 获奖情况详细内容 =====
document_xml = replace_in_wt(document_xml, '普通话一级甲等；', '· 全国大学生数学竞赛（非数学类B类）  [浙江省一等奖]\n')
document_xml = replace_in_wt(document_xml, '大学英语四/六级（CET-4/6），良好的听说读写能力，快速浏览英语专业文件及书籍；', '· 浙江省微积分竞赛  [三等奖]\n')
document_xml = replace_in_wt(document_xml, '通过全国计算机二级考试，熟练运用office相关软件。', '· 浙江大学丹青学园团总支篮球赛  [团体第一名]\n· CET-4 / CET-6 英语等级测试  [已通过]\n· 高中阶段  [多次获评校级三好学生]')

# ===== 自我评价详细内容 =====
old_self = '深度互联网从业人员，对互联网保持高度的敏感性和关注度，熟悉产品开发流程，有很强的产品规划、需求分析、交互设计能力，能独立承担APP和WEB项目的管控工作，善于沟通，贴近用户。'
new_self = '本科在读，主修信息管理与信息系统专业。关注数据分析、运筹优化与数学建模方向，具备扎实的数学基础和逻辑思维能力。\n· 数据分析：关注统计学习、机器学习在商业决策中的应用\n· 运筹优化：研究数学规划、优化算法，应用于供应链管理等实际问题\n· 数学建模：具备扎实的数学基础，致力于跨学科的建模挑战和实际问题求解'
document_xml = replace_in_wt(document_xml, old_self, new_self)

# ===== 第二段实习（高中） =====
# 注意：必须先替换"2010.03-2012.03"，再替换"2012"，否则"2010.03-2012.03"中的"2012"会被提前替换
document_xml = replace_in_wt(document_xml, '2010.03-2012.03          ', '2021.09-2024.06          ')
document_xml = replace_in_wt(document_xml, '软件工程师', '理科高中')
document_xml = replace_in_wt(document_xml, '负责公司业务系统的设计及改进，参与公司网上商城系统产品功能设计及实施工作。', '高中阶段，培养了扎实的数学和逻辑思维能力。')
document_xml = replace_in_wt(document_xml, '负责客户调研、客户需求分析、方案写作等工作， 参与公司多个大型电子商务项目的策划工作，担任大商集团网上商城一期建设项目经理。', '多次获评校级三好学生，具备良好的学习能力和团队协作精神。')

# ===== 第二段实习内容 =====
document_xml = replace_in_wt(document_xml, '2012', '2024')
document_xml = replace_in_wt(document_xml, '04-至今        ', '09-至今        ')
document_xml = replace_in_wt(document_xml, '市场营销（实习生）', '信息管理与信息系统专业')
document_xml = replace_in_wt(document_xml, '负责公司线上端资源的销售工作（以开拓客户为主），公司主要资源以广点通、智汇推、百度、小米、', '主修数据结构、数据库系统、运筹学、数据分析等课程，')
document_xml = replace_in_wt(document_xml, '360', '')
document_xml = replace_in_wt(document_xml, '、沃门户等；', '')
document_xml = replace_in_wt(document_xml, '实时了解行业的变化，跟踪客户的详细数据，为客户制定更完善的投放计划（合作过珍爱网、世纪佳缘、', '具备扎实的数学和计算机基础，')
document_xml = replace_in_wt(document_xml, '56', '')
document_xml = replace_in_wt(document_xml, '视频、京东等客户）', '致力于数据驱动的管理优化研究。')


# ========== 保存 ==========
template_files['word/document.xml'] = document_xml.encode('utf-8')

output_path = os.path.join(os.path.dirname(__file__), '鲁振哲_个人简历_new.docx')
# 如果文件存在，先删除
if os.path.exists(output_path):
    os.remove(output_path)
    
output = BytesIO()
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zout:
    for item_name, item_data in template_files.items():
        zout.writestr(item_name, item_data)

with open(output_path, 'wb') as f:
    f.write(output.getvalue())

print(f'\n简历已生成: {output_path}')
