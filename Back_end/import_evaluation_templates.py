import re
from database import SessionLocal
from models import EvaluationTemplate, TemplateStep, TemplateScorePoint

def parse_evaluation_templates(file_path):
    """解析人教版.txt文件，提取评价模板数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    parsed_templates = []
    current_template = None
    current_step = None
    current_score_point = None
    
    for line in lines:
        # 保留原始缩进，用于判断行的层级
        original_line = line
        line = line.strip()
        
        # 检查是否是新的评价表开始
        if '评价表' in line:
            # 保存当前评价表（如果存在）
            if current_template:
                # 保存当前步骤（如果存在）
                if current_step:
                    if current_score_point:
                        current_step['score_points'].append(current_score_point)
                    current_template['steps'].append(current_step)
                parsed_templates.append(current_template)
            
            # 开始新的评价表
            current_template = {
                'template_name': line,
                'description': '',
                'is_default': True,
                'steps': []
            }
            current_step = None
            current_score_point = None
        
        # 检查是否是新的大步骤开始
        elif line.startswith(('一、', '二、', '三、', '四、', '五、')):
            # 保存当前步骤（如果存在）
            if current_step:
                if current_score_point:
                    current_step['score_points'].append(current_score_point)
                current_template['steps'].append(current_step)
            
            # 开始新的步骤
            current_step = {
                'step_name': line,
                'step_order': len(current_template['steps']) + 1,
                'score_points': []
            }
            current_score_point = None
        
        # 检查是否是新的得分点名称（缩进两个空格）
        elif len(original_line) - len(original_line.lstrip()) == 2 and line and not line.startswith(('评分标准：', '分值：', '扣分点说明：')):
            # 保存当前得分点（如果存在）
            if current_score_point:
                current_step['score_points'].append(current_score_point)
            
            # 开始新的得分点
            current_score_point = {
                'point_name': line,
                'scoring_criteria': '',
                'score': 0,
                'deduction_description': '',
                'point_order': len(current_step['score_points']) + 1
            }
        
        # 检查是否是评分标准
        elif line.startswith('评分标准：'):
            if current_score_point:
                current_score_point['scoring_criteria'] = line[5:]  # 去掉"评分标准："
        
        # 检查是否是分值
        elif line.startswith('分值：'):
            if current_score_point:
                # 提取分值数字
                score_match = re.search(r'\d+', line)
                if score_match:
                    current_score_point['score'] = int(score_match.group())
        
        # 检查是否是扣分点说明
        elif line.startswith('扣分点说明：'):
            if current_score_point:
                current_score_point['deduction_description'] = line[6:]
    
    # 保存最后一个评价表
    if current_template:
        if current_step:
            if current_score_point:
                current_step['score_points'].append(current_score_point)
            current_template['steps'].append(current_step)
        parsed_templates.append(current_template)
    
    return parsed_templates

def import_templates_to_db(templates):
    """将解析后的评价模板数据导入到数据库"""
    db = SessionLocal()
    
    try:
        # 清空现有数据
        print("清空现有评价模板数据...")
        # 先删除exams表中的数据，因为它有外键引用evaluation_templates
        from models import Exam
        db.query(Exam).delete()
        # 然后删除评价模板相关数据
        db.query(TemplateScorePoint).delete()
        db.query(TemplateStep).delete()
        db.query(EvaluationTemplate).delete()
        db.commit()
        print("数据清空完成")
        
        # 导入新数据
        print(f"开始导入 {len(templates)} 个评价模板...")
        
        for template_data in templates:
            # 创建评价模板
            template = EvaluationTemplate(
                template_name=template_data['template_name'],
                description=template_data['description'],
                creator_id="13900139000",  # 使用教师账号的电话作为creator_id
                is_default=template_data['is_default']
            )
            db.add(template)
            db.flush()  # 获取模板ID
            
            # 添加步骤
            for step_data in template_data['steps']:
                step = TemplateStep(
                    template_id=template.id,
                    step_name=step_data['step_name'],
                    step_order=step_data['step_order']
                )
                db.add(step)
                db.flush()  # 获取步骤ID
                
                # 添加评分点
                for point_data in step_data['score_points']:
                    score_point = TemplateScorePoint(
                        step_id=step.id,
                        point_name=point_data['point_name'],
                        scoring_criteria=point_data['scoring_criteria'],
                        score=point_data['score'],
                        deduction_description=point_data['deduction_description'],
                        point_order=point_data['point_order']
                    )
                    db.add(score_point)
        
        db.commit()
        print("评价模板导入完成！")
        
    except Exception as e:
        print(f"导入过程中出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "人教版_格式化.txt")
    print(f"解析 {file_path} 文件...")
    templates = parse_evaluation_templates(file_path)
    print(f"解析完成，共提取 {len(templates)} 个评价模板")
    
    import_templates_to_db(templates)
