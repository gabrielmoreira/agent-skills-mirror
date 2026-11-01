---
name: achievement-qztc
description: 课程目标达成情况分析表生成工具。根据Excel学生数据替换Word模板中的课程目标达成情况，生成新的分析表。
---

# 课程目标达成情况分析表生成工具（QZTC版）

根据Excel学生数据替换Word模板中的课程目标达成情况，生成新的分析表。

## 适用场景

- 根据Excel学生名单生成课程目标达成情况分析表
- 自动计算各课程目标的达成值（随机生成成绩，百分比表示）

---

## 文件路径

- **模板文件**: `/Volumes/qztcm09/Desktop/temp/课程目标达成情况分析表-数据可视化-模版.docx`
- **Excel数据**: `/Volumes/qztcm09/Desktop/temp/数据可视化技术23级计算机.xls`

---

## 使用步骤

### 步骤1：读取Excel数据

```python
import pandas as pd
import shutil
import random
from docx import Document
from datetime import datetime

# 读取Excel
df = pd.read_excel('/Users/qztcm09/Desktop/temp/数据可视化技术23级计算机.xls')

# 排除旷考学生
df = df[df['备注'] != '旷考'].reset_index(drop=True)

# 自动判断当前学年和学期
now = datetime.now()
year = now.year
month = now.month
day= now.day

if 1 <= month <= 6:
    # 1-6月：第一学期（上学年）
    academic_year = f"{year-1} - {year}"
    semester = "一"
else:
    # 7-12月：第二学期（上学年）
    academic_year = f"{year-1} - {year}"
    semester = "二"

print(f"当前学年: {academic_year}, 学期: {semester}学期")

# 从"班级"字段提取年级、班级、专业信息
# 专业名称提取支持两种情况：
#   情况1: "23级计算机" → 年级=23, 专业=计算机
#   情况2: "23级软工2班" → 年级=23, 专业=软工
import re
class_name = df['班级'].iloc[0] if '班级' in df.columns else ''
match = re.search(r'(\d+)级', str(class_name))
grade = match.group(1) if match else ''  # 如 "23"
# 提取专业：匹配 "XX级" 后面到 "XX班" 或结尾的部分
match = re.search(r'\d+级(.+?)(?:\d+班)?$', str(class_name))
major = match.group(1).strip() if match else ''  # 如 "计算机" 或 "软工"


# 获取学生信息
students = df[['学号', '姓名']].copy()
print(f"学生人数: {len(students)}")
```

### 步骤2：复制模板并打开

```python
template_path = '/Users/qztcm09/Desktop/temp/课程目标达成情况分析表-数据可视化-模版.docx'
output_path = '/Users/qztcm09/Desktop/temp/课程目标达成情况分析表-数据可视化-23级计算机.docx'

shutil.copy(template_path, output_path)
doc = Document(output_path)
```

### 步骤3：通用文本替换

**⚠️ 重要：Word占位符可能被拆分成多个run，且表格单元格中可能有换行，需要特殊处理，保留原格式**

```python
def replace_text_preserve_format(para, replacements):
    """替换段落文本但保留格式"""
    # 先收集所有run的文本
    full_text = ''.join(run.text for run in para.runs if run.text)
    
    # 检查是否有占位符
    has_placeholder = any(old in full_text for old, _ in replacements)
    if not has_placeholder:
        return
    
    # 执行替换
    for old, new in replacements:
        full_text = full_text.replace(old, new)
    
    # 获取第一个run的格式作为基准
    if para.runs:
        first_run = para.runs[0]
        font_name = first_run.font.name
        font_size = first_run.font.size
        font_bold = first_run.font.bold
        font_italic = first_run.font.italic
    else:
        font_name, font_size, font_bold, font_italic = None, None, None, None
    
    # 清空并用新文本创建单一run，保留格式
    para.clear()
    run = para.add_run(full_text)
    if font_name:
        run.font.name = font_name
    if font_size:
        run.font.size = font_size
    if font_bold is not None:
        run.font.bold = font_bold
    if font_italic is not None:
        run.font.italic = font_italic
    
    return para

def replace_text_in_table_cell(cell, replacements):
    """替换表格单元格中的文本（处理单元格内换行的情况）"""
    # 遍历单元格中的所有段落
    for para in cell.paragraphs:
        full_text = ''.join(run.text for run in para.runs if run.text)
        has_placeholder = any(old in full_text for old, _ in replacements)
        
        if has_placeholder:
            # 获取格式
            if para.runs:
                first_run = para.runs[0]
                font_name = first_run.font.name
                font_size = first_run.font.size
                font_bold = first_run.font.bold
                font_italic = first_run.font.italic
            else:
                font_name, font_size, font_bold, font_italic = None, None, None, None
            
            # 执行替换
            for old, new in replacements:
                full_text = full_text.replace(old, new)
            
            # 清空并重新设置
            para.clear()
            run = para.add_run(full_text)
            if font_name:
                run.font.name = font_name
            if font_size:
                run.font.size = font_size
            if font_bold is not None:
                run.font.bold = font_bold
            if font_italic is not None:
                run.font.italic = font_italic
    
    return cell

# 替换配置
replacements = [
    ('$acyear$', academic_year),
    ('$semester$', semester),
    ('$g$', grade),
    ('$major$', major),
    ('$total$', f'{len(students)}人'),
    ('$year$', str(year)),
    ('$month$', str(month)),
    ('$day$', str(day)),
]

# 替换表格中的文本
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            replace_text_in_cell(cell, replacements)

# 替换段落中的文本（处理被拆分的情况，保留格式）
for para in doc.paragraphs:
    replace_text_preserve_format(para, replacements)
```

### 步骤4：更新表8 - 课程目标个体达成情况明细

**重要**：
1. 先清理除表头（2行）和最后一行（平均值）外的所有学生数据
2. 根据Excel学生数动态调整表格行数
3. **在最后一行（平均值行）之前插入新行**
4. 所有达成值用**百分比**表示（如 66%）

**表格索引**: 8

**表头结构**（前2行）:
- 行0: 序号 | 学号 | 姓名 | 课程目标1(25分) | 课程目标1 | 课程目标2(30分) | 课程目标2 | 课程目标3(26.5分) | 课程目标3 | 课程目标4(18.5分) | 课程目标4
- 行1: 序号 | 学号 | 姓名 | 得分 | 达成值 | 得分 | 达成值 | 得分 | 达成值 | 得分 | 达成值

**数据列对应关系**:
| 列索引 | 内容 |
|--------|------|
| 0 | 序号 |
| 1 | 学号 |
| 2 | 姓名 |
| 3 | 随机值 a (10-24)，课程目标1得分 |
| 4 | a/25*100%，课程目标1达成值（百分比） |
| 5 | 随机值 b (20-28)，课程目标2得分 |
| 6 | b/30*100%，课程目标2达成值（百分比） |
| 7 | 随机值 c (20-25)，课程目标3得分 |
| 8 | c/26.5*100%，课程目标3达成值（百分比） |
| 9 | 随机值 d (15-18)，课程目标4得分 |
| 10 | d/18.5*100%，课程目标4达成值（百分比） |

```python
# 步骤4.1: 动态调整表格行数（在平均值行之前插入）
table = doc.tables[8]
current_rows = len(table.rows)
# 当前模板可以容纳的学生数（去掉2行表头和1行平均值）
template_capacity = current_rows - 3

# 调整行数：在倒数第2行（平均值行之前）插入
if len(students) > template_capacity:
    # 需要插入行，在平均值行之前插入
    for i in range(len(students) - template_capacity):
        # 在倒数第2行之前插入（即平均值行之前）
        new_row = table.add_row()
        # 将新行移动到平均值行之前
        # 由于add_row()是添加到末尾，需要交换位置
        # 获取平均值行索引
        avg_idx = len(table.rows) - 1
        # 将新插入的行移到平均值行之前
        table._element.remove(new_row._element)
        table._element.insert(len(table.rows) - 2, new_row._element)
elif len(students) < template_capacity:
    # 需要删除多余行（从数据区域末尾开始删，保留平均值行）
    for i in range(template_capacity - len(students)):
        # 删除倒数第2行（最后一个数据行）
        delete_idx = 2 + len(students)
        if delete_idx < len(table.rows) - 1:
            table._element.remove(table.rows[delete_idx]._element)

# 步骤4.2: 清理数据行（保留前2行表头和最后1行平均值）
for row_idx in range(2, len(table.rows) - 1):
    for cell in table.rows[row_idx].cells:
        cell.text = ''

# 步骤4.3: 填入学生数据（达成值用百分比）
all_a, all_b, all_c, all_d = [], [], [], []
student_data = []

for i, (_, student) in enumerate(students.iterrows()):
    row_idx = i + 2
    if row_idx >= len(table.rows) - 1:
        break
    
    row = table.rows[row_idx]
    a = random.randint(10, 24)
    b = random.randint(20, 28)
    c = random.randint(20, 25)
    d = random.randint(15, 18)
    
    all_a.append(a)
    all_b.append(b)
    all_c.append(c)
    all_d.append(d)
    
    # 转为百分比
    v1, v2, v3, v4 = a/25*100, b/30*100, c/26.5*100, d/18.5*100
    student_data.append({'v1': v1, 'v2': v2, 'v3': v3, 'v4': v4})
    
    row.cells[0].text = str(i + 1)
    row.cells[1].text = str(student['学号'])
    row.cells[2].text = student['姓名']
    row.cells[3].text = f"{a:.2f}"
    row.cells[4].text = f"{v1:.0f}%"  # 百分比
    row.cells[5].text = f"{b:.2f}"
    row.cells[6].text = f"{v2:.0f}%"  # 百分比
    row.cells[7].text = f"{c:.2f}"
    row.cells[8].text = f"{v3:.0f}%"  # 百分比
    row.cells[9].text = f"{d:.2f}"
    row.cells[10].text = f"{v4:.0f}%"  # 百分比

n = len(student_data)

# 步骤4.4: 最后一行填写平均值（百分比）
avg_row = table.rows[-1]
avg_a = sum(all_a) / n
avg_b = sum(all_b) / n
avg_c = sum(all_c) / n
avg_d = sum(all_d) / n
avg_v1 = sum(s['v1'] for s in student_data) / n
avg_v2 = sum(s['v2'] for s in student_data) / n
avg_v3 = sum(s['v3'] for s in student_data) / n
avg_v4 = sum(s['v4'] for s in student_data) / n

avg_row.cells[0].text = "平均值"
avg_row.cells[3].text = f"{avg_a:.2f}"
avg_row.cells[4].text = f"{avg_v1:.0f}%"
avg_row.cells[5].text = f"{avg_b:.2f}"
avg_row.cells[6].text = f"{avg_v2:.0f}%"
avg_row.cells[7].text = f"{avg_c:.2f}"
avg_row.cells[8].text = f"{avg_v3:.0f}%"
avg_row.cells[9].text = f"{avg_d:.2f}"
avg_row.cells[10].text = f"{avg_v4:.0f}%"
```

### 步骤5：更新表7汇总数据（百分比）

```python
table7 = doc.tables[7]
table7.rows[5].cells[7].text = f"{avg_v1:.0f}%"
table7.rows[8].cells[7].text = f"{avg_v2:.0f}%"
table7.rows[11].cells[7].text = f"{avg_v3:.0f}%"
table7.rows[14].cells[7].text = f"{avg_v4:.0f}%"
```

### 步骤6：更新课程目标分析段落（百分比）

```python
# 计算统计数据
max_v1 = max(s['v1'] for s in student_data)
min_v1 = min(s['v1'] for s in student_data)
# ... 其他目标类似

# 计算满足百分比阈值的学生比例
count_v1_80 = sum(1 for s in student_data if s['v1'] >= 80)
count_v1_60 = sum(1 for s in student_data if s['v1'] >= 60)
# ... 其他类似

pct_v1_80 = count_v1_80 / n * 100
pct_v1_60 = count_v1_60 / n * 100
# ... 其他类似

# 更新段落
new_texts = {
    1: f"课程目标1的平均达成值为{avg_v1:.0f}%，最高达成值为{max_v1:.0f}%，最低达成值为{min_v1:.0f}%。其中{pct_v1_80:.1f}%的学生达成值在80%以上，{pct_v1_60:.1f}%的学生达成值在60%以上，说明...",
    # ... 其他目标
}

# 找到并更新段落
for i, para in enumerate(doc.paragraphs):
    if '课程目标1的平均达成值为' in para.text:
        # 更新段落文本
        break
```

### 步骤7：保存

```python
doc.save(output_path)
print(f"文件已保存至: {output_path}")
```

---

## 完整代码示例

```python
import pandas as pd
import shutil
import random
from docx import Document
from datetime import datetime

random.seed(42)  # 可选：固定随机种子

def replace_text_preserve_format(para, replacements):
    """替换段落文本但保留格式"""
    # 先收集所有run的文本
    full_text = ''.join(run.text for run in para.runs if run.text)
    
    # 检查是否有占位符
    has_placeholder = any(old in full_text for old, _ in replacements)
    if not has_placeholder:
        return
    
    # 执行替换
    for old, new in replacements:
        full_text = full_text.replace(old, new)
    
    # 获取第一个run的格式作为基准
    if para.runs:
        first_run = para.runs[0]
        font_name = first_run.font.name
        font_size = first_run.font.size
        font_bold = first_run.font.bold
        font_italic = first_run.font.italic
    else:
        font_name, font_size, font_bold, font_italic = None, None, None, None
    
    # 清空并用新文本创建单一run，保留格式
    para.clear()
    run = para.add_run(full_text)
    if font_name:
        run.font.name = font_name
    if font_size:
        run.font.size = font_size
    if font_bold is not None:
        run.font.bold = font_bold
    if font_italic is not None:
        run.font.italic = font_italic
    
    return para

def replace_text_in_table_cell(cell, replacements):
    """替换表格单元格中的文本（处理单元格内换行的情况）"""
    for para in cell.paragraphs:
        full_text = ''.join(run.text for run in para.runs if run.text)
        has_placeholder = any(old in full_text for old, _ in replacements)
        
        if has_placeholder:
            if para.runs:
                first_run = para.runs[0]
                font_name = first_run.font.name
                font_size = first_run.font.size
                font_bold = first_run.font.bold
                font_italic = first_run.font.italic
            else:
                font_name, font_size, font_bold, font_italic = None, None, None, None
            
            for old, new in replacements:
                full_text = full_text.replace(old, new)
            
            para.clear()
            run = para.add_run(full_text)
            if font_name:
                run.font.name = font_name
            if font_size:
                run.font.size = font_size
            if font_bold is not None:
                run.font.bold = font_bold
            if font_italic is not None:
                run.font.italic = font_italic
    
    return cell

def generate_achievement_analysis():
    # 1. 读取Excel
    df = pd.read_excel('/Users/qztcm09/Desktop/temp/数据可视化技术23级计算机.xls')
    df = df[df['备注'] != '旷考'].reset_index(drop=True)
    students = df[['学号', '姓名']].copy()
    print(f"学生人数: {len(students)}")
    
    # 2. 复制模板
    template_path = '/Users/qztcm09/Desktop/temp/课程目标达成情况分析表-数据可视化-模版.docx'
    output_path = '/Users/qztcm09/Desktop/temp/课程目标达成情况分析表-数据可视化-23级计算机.docx'
    shutil.copy(template_path, output_path)
    doc = Document(output_path)
    
    # 3. 通用文本替换
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    
    # 根据班级提取专业信息（支持两种情况）
    # 情况1: "23级计算机" → 专业="计算机"
    # 情况2: "23级软工2班" → 专业="软工"
    import re
    class_name = df['班级'].iloc[0] if '班级' in df.columns else ''
    match = re.search(r'(\d+)级', str(class_name))
    grade = match.group(1) if match else ''
    match = re.search(r'\d+级(.+?)(?:\d+班)?$', str(class_name))
    major = match.group(1).strip() if match else ''
    
    if 1 <= month <= 6:
        academic_year = f"{year-1} - {year}"
        semester = "一"
    else:
        academic_year = f"{year-1} - {year}"
        semester = "二"
    
    replacements = [
        ('$acyear$', academic_year),
        ('$semester$', semester),
        ('$g$', grade),
        ('$major$', major),
        ('$total$', f'{len(students)}人'),
        ('$year$', str(year)),
        ('$month$', str(month)),
        ('$day$', str(day)),
    ]
    
    # 替换表格中的文本（使用新的函数处理换行）
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                replace_text_in_table_cell(cell, replacements)
    
    # 替换段落中的文本（保留格式）
    for para in doc.paragraphs:
        replace_text_preserve_format(para, replacements)
    
    # 4. 更新表8
    table = doc.tables[8]
    current_rows = len(table.rows)
    template_capacity = current_rows - 3
    
    # 调整行数
    if len(students) > template_capacity:
        # 需要插入行，在平均值行之前插入
        rows_to_add = len(students) - template_capacity
        for i in range(rows_to_add):
            # 在倒数第2行（平均值行之前）插入新行
            new_row = table.add_row()
            # 将新行从末尾移到平均值行之前
            avg_idx = len(table.rows) - 1
            # 获取新行的tr元素
            new_tr = new_row._element
            # 移除
            table._element.remove(new_tr)
            # 在平均值行之前插入
            table._element.insert(avg_idx, new_tr)
        print(f"插入{rows_to_add}行")
    elif len(students) < template_capacity:
        # 需要删除多余行
        rows_to_remove = template_capacity - len(students)
        for i in range(rows_to_remove):
            delete_idx = 2 + len(students)
            if delete_idx < len(table.rows) - 1:
                table._element.remove(table.rows[delete_idx]._element)
        print(f"删除{rows_to_remove}行")
    
    # 清理数据行
    for row_idx in range(2, len(table.rows) - 1):
        for cell in table.rows[row_idx].cells:
            cell.text = ''
    
    # 填入数据
    all_a, all_b, all_c, all_d = [], [], [], []
    student_data = []
    
    for i, (_, student) in enumerate(students.iterrows()):
        row_idx = i + 2
        if row_idx >= len(table.rows) - 1:
            break
        
        row = table.rows[row_idx]
        a = random.randint(10, 24)
        b = random.randint(20, 28)
        c = random.randint(20, 25)
        d = random.randint(15, 18)
        
        all_a.append(a)
        all_b.append(b)
        all_c.append(c)
        all_d.append(d)
        
        v1, v2, v3, v4 = a/25*100, b/30*100, c/26.5*100, d/18.5*100
        student_data.append({'v1': v1, 'v2': v2, 'v3': v3, 'v4': v4})
        
        row.cells[0].text = str(i + 1)
        row.cells[1].text = str(student['学号'])
        row.cells[2].text = student['姓名']
        row.cells[3].text = f"{a:.2f}"
        row.cells[4].text = f"{v1:.0f}%"
        row.cells[5].text = f"{b:.2f}"
        row.cells[6].text = f"{v2:.0f}%"
        row.cells[7].text = f"{c:.2f}"
        row.cells[8].text = f"{v3:.0f}%"
        row.cells[9].text = f"{d:.2f}"
        row.cells[10].text = f"{v4:.0f}%"
    
    n = len(student_data)
    
    # 平均值（最后一行）
    avg_row = table.rows[-1]
    avg_a = sum(all_a) / n
    avg_b = sum(all_b) / n
    avg_c = sum(all_c) / n
    avg_d = sum(all_d) / n
    avg_v1 = sum(s['v1'] for s in student_data) / n
    avg_v2 = sum(s['v2'] for s in student_data) / n
    avg_v3 = sum(s['v3'] for s in student_data) / n
    avg_v4 = sum(s['v4'] for s in student_data) / n
    
    avg_row.cells[0].text = "平均值"
    avg_row.cells[1].text = ""
    avg_row.cells[2].text = ""
    avg_row.cells[3].text = f"{avg_a:.2f}"
    avg_row.cells[4].text = f"{avg_v1:.0f}%"
    avg_row.cells[5].text = f"{avg_b:.2f}"
    avg_row.cells[6].text = f"{avg_v2:.0f}%"
    avg_row.cells[7].text = f"{avg_c:.2f}"
    avg_row.cells[8].text = f"{avg_v3:.0f}%"
    avg_row.cells[9].text = f"{avg_d:.2f}"
    avg_row.cells[10].text = f"{avg_v4:.0f}%"
    
    # 5. 更新表7
    table7 = doc.tables[7]
    table7.rows[5].cells[7].text = f"{avg_v1:.0f}%"
    table7.rows[8].cells[7].text = f"{avg_v2:.0f}%"
    table7.rows[11].cells[7].text = f"{avg_v3:.0f}%"
    table7.rows[14].cells[7].text = f"{avg_v4:.0f}%"
    
    # 6. 统计并更新段落（见步骤6）
    # ...
    
    # 7. 保存
    doc.save(output_path)
    print(f"完成！文件已保存至: {output_path}")

if __name__ == '__main__':
    generate_achievement_analysis()
```

---

## ⚠️ 注意事项

### 1. 达成值格式
- 所有达成值使用**百分比**表示（如 66%、85%）
- 得分保持原始数值（如 16.50）

### 2. 表格行数调整
- 模板容量 = 表格总行数 - 2（表头）- 1（平均值）
- **学生数多：在平均值行之前插入新行**
- 学生数少：删除多余的数据行

### 3. 随机成绩范围
| 课程目标 | 得分范围 | 满分 | 达成值计算 |
|----------|----------|------|------------|
| 目标1 | 10-24 | 25| a/25*100% |
| 目标2 | 20-29 | 30 | b/30*100% |
| 目标3 | 20-25 | 26.5 | c/26.5*100% |
| 目标4 | 15-18 | 18.5 | d/18.5*100% |

### 4. 模板预处理
使用前确保模板已修正：
- 去除黄色高亮
- 修正占位符（如 major$ → $major$）
- 扩展表8容量（如需要）
