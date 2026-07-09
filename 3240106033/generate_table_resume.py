#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于表格简历模板生成个人简历 - 精确替换模板中的占位文本
使用XML解析方式，精确定位到每个单元格
"""

import json
import os
import sys
import zipfile
import re
from io import BytesIO

# ========== 数据 ==========
INFO_PATH = os.path.join(os.path.dirname(__file__), 'src', 'public', 'info.json')
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '简历表格-空白表格简历模板.docx')

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

def replace_in_wt_after(xml, after_text, old_text, new_text):
    """在指定文本之后，在w:t标签内替换文本"""
    pos = xml.find(after_text)
    if pos < 0:
        print(f'  NO 未找到锚点: "{after_text}"')
        return xml
    
    # 在锚点之后查找
    pattern = re.compile(r'(<w:t[^>]*>)' + re.escape(old_text) + r'(</w:t>)')
    match = pattern.search(xml, pos + len(after_text))
    if match:
        xml = xml[:match.start(1)] + match.group(1) + new_text + match.group(2) + xml[match.end(2):]
        print(f'  OK 替换: "{old_text}" -> "{new_text}" (在"{after_text}"之后)')
    else:
        print(f'  NO 未找到: "{old_text}" (在"{after_text}"之后)')
    return xml

# ===== 个人信息 =====

# 姓名：张某某 -> 鲁振哲
# "张"和"某某"在不同w:t标签中
document_xml = replace_in_wt(document_xml, '张', '鲁')
document_xml = replace_in_wt(document_xml, '某某', '振哲')

# 性别：男（不变）

# 出生年月：1994.02 -> 2006年
# "出生"和"年月"在不同w:t标签中，"199"、"4"、".02"也在不同标签中
# 使用"出生"作为锚点
document_xml = replace_in_wt_after(document_xml, '出生', '199', '200')
document_xml = replace_in_wt_after(document_xml, '200', '4', '6')
document_xml = replace_in_wt_after(document_xml, '2006', '.02', '年')

# 民族：汉族（不变）

# 身高：172cm -> 178cm
# "1"、"7"、"2cm" 在不同w:t标签中
# 使用"身"作为锚点（"身  高"有空格）
document_xml = replace_in_wt_after(document_xml, '身', '1', '1')  # 第一个"1"不变
document_xml = replace_in_wt_after(document_xml, '身', '7', '7')  # "7"不变
document_xml = replace_in_wt_after(document_xml, '身', '2cm', '8cm')

# 政治面貌：预备党员 -> 共青团员
document_xml = replace_in_wt(document_xml, '预备党员', '共青团员')

# 手机：000-000-0000 -> 131 9968 3838
document_xml = replace_in_wt(document_xml, '000-000-0000', '131 9968 3838')

# 最高学历：本科（不变）

# E-mail：第二个"000-000-0000"是邮箱，上面的替换已处理

# QQ/微信 -> 填写QQ号（保持原样）

# 求职意向：小学语文老师 -> 数据分析/运筹优化
document_xml = replace_in_wt(document_xml, ' 小学语文老师', ' 数据分析/运筹优化')

# ===== 教育经历 =====
document_xml = replace_in_wt(document_xml, '2016.09 - 2020.06', '2024.09 - 至今')
document_xml = replace_in_wt(document_xml, '山东理工', '浙江')
document_xml = replace_in_wt(document_xml, '大学', '大学')  # 保持"大学"不变
document_xml = replace_in_wt(document_xml, '汉语言文学', '信息管理与信息系统')
document_xml = replace_in_wt(document_xml, '专业课程平均成绩93.4分，专业排名TOP3%。', '')
document_xml = replace_in_wt(document_xml, '主修课程：古代汉语、现当代汉语、外国文学、教育学原理等。', '主修课程：数据结构、数据库系统、运筹学、数据分析、管理信息系统、统计学、会计学、经济学')

# ===== 工作经历 =====
# 第一段工作经历（学生工作）
document_xml = replace_in_wt(document_xml, '2019.03 - 2019.07', '2024.09 - 至今')
document_xml = replace_in_wt(document_xml, '临沂', '管理学院学业指导中心')
document_xml = replace_in_wt(document_xml, '中学', '')
document_xml = replace_in_wt(document_xml, '语文老师', '干事')
document_xml = replace_in_wt(document_xml, '担任语文教学，养成写教学反思的良好习惯，丰富了教学经验，提升了教学能和处理课堂突发事件的能力。班主任工作使我提升了与家长沟通的能力，增加了管理班级的经验，更加能吃苦耐劳。', '参与管理学院学业指导中心的日常运营与活动组织工作，协助开展学业帮扶、经验分享等活动。')
document_xml = replace_in_wt(document_xml, '对学生有爱心有耐心，表现突出被评为\u201c优秀班主任\u201d。', '协助整理学业指导资料，为学院同学提供学习支持与服务。')

# 第二段工作经历（高中）
document_xml = replace_in_wt(document_xml, '2018.07 - 2018.09', '2021.09 - 2024.06')
document_xml = replace_in_wt(document_xml, '学会', '理科')
document_xml = replace_in_wt(document_xml, '教育', '高中')
document_xml = replace_in_wt(document_xml, '兼职教师', '学生')

# 第三段工作经历（删除）
document_xml = replace_in_wt(document_xml, '2017.07 - 2017.09', '')
document_xml = replace_in_wt(document_xml, '西安', '')
document_xml = replace_in_wt(document_xml, '外语学校', '')
document_xml = replace_in_wt(document_xml, '兼职教师', '')

# ===== 获得奖项 =====
document_xml = replace_in_wt(document_xml, '连续3个学年获得校一级奖学金，2017.12获院学生会优秀干事称号', '· 全国大学生数学竞赛（非数学类B类）  [浙江省一等奖]')
document_xml = replace_in_wt(document_xml, '2018荣获第七届全国大学生文学作品大赛三等奖', '· 浙江省微积分竞赛  [三等奖]')
document_xml = replace_in_wt(document_xml, '2016-2017年度被评为\u201c校级社团活动积极分子\u201d', '· 浙江大学丹青学园团总支篮球赛  [团体第一名]\n· CET-4 / CET-6 英语等级测试  [已通过]\n· 高中阶段  [多次获评校级三好学生]')

# ===== 技能证书 =====
document_xml = replace_in_wt(document_xml, '普通话二级甲等       大学英语四级', 'CET-4 / CET-6 英语等级测试  [已通过]')
document_xml = replace_in_wt(document_xml, '教师资格证           心理咨询师资格证初级', '全国大学生数学竞赛  [浙江省一等奖]')

# ===== 自我评价 =====
document_xml = replace_in_wt(document_xml, '热爱教师这份神圣的职业，喜欢和学生们相处，耐心、细心，学会从每个细节关心学生，事无巨细。喜欢在工作过程中探索、收获新的教学方法，逐步形成了自己的教育教学理念，注重学生团队和团体。', '本科在读，主修信息管理与信息系统专业。关注数据分析、运筹优化与数学建模方向，具备扎实的数学基础和逻辑思维能力。')
document_xml = replace_in_wt(document_xml, '性格开朗，勤奋稳重，具有很好的团队合作精神；严格要求，追求上进，生活作风严谨，待人诚恳，有很强的荣誉感及团队合作精神。', '· 数据分析：关注统计学习、机器学习在商业决策中的应用\n· 运筹优化：研究数学规划、优化算法，应用于供应链管理等实际问题')
document_xml = replace_in_wt(document_xml, '热爱文学，具有一定的文学功底和良好的文学感知能力。', '· 数学建模：具备扎实的数学基础，致力于跨学科的建模挑战和实际问题求解')

# ========== 保存 ==========
template_files['word/document.xml'] = document_xml.encode('utf-8')

output_path = os.path.join(os.path.dirname(__file__), '鲁振哲_表格简历.docx')
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
