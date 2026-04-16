#工具文件：实验匹配器
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import EvaluationTemplate, TemplateStep, TemplateScorePoint
from similarity import ExperimentMatcher

class DatabaseExperimentMatcher:
    def __init__(self):
        self.matcher = None
        self.templates = []
        self.load_templates()
    
    def load_templates(self):
        """从数据库加载评价模板数据"""
        db = SessionLocal()
        try:
            # 加载所有评价模板，包括关联的步骤和评分点
            templates = db.query(EvaluationTemplate).all()
            experiments = []
            
            for template in templates:
                # 构建模板内容
                content = f"# {template.template_name}\n"
                if template.description:
                    content += f"## 模板描述\n{template.description}\n\n"
                
                # 按步骤顺序排序
                steps = sorted(template.steps, key=lambda x: x.step_order)
                
                for step in steps:
                    content += f"## {step.step_name}\n"
                    
                    # 按评分点顺序排序
                    score_points = sorted(step.score_points, key=lambda x: x.point_order)
                    
                    for point in score_points:
                        if point.point_name:
                            content += f"### {point.point_name} ({point.score}分)\n"
                        else:
                            content += f"### 评分点 ({point.score}分)\n"
                        if point.scoring_criteria:
                            content += f"评分标准: {point.scoring_criteria}\n"
                        content += f"扣分点说明: {point.deduction_description}\n\n"
                
                experiments.append({
                    'id': template.id,
                    'template_name': template.template_name,
                    'title': template.template_name,  # 保持与原接口兼容
                    'content': content,
                    'is_default': template.is_default
                })
            
            self.templates = experiments
            self.matcher = ExperimentMatcher(experiments)
        except Exception as e:
            print(f"加载模板数据时出错: {e}")
        finally:
            db.close()
    
    def find_most_similar_experiment(self, user_input):
        """根据用户输入的实验名称，找到最相似的评价模板"""
        if not self.matcher:
            self.load_templates()
        
        if not self.matcher:
            return None
        
        result = self.matcher.find_most_similar(user_input)
        if result:
            # 增强返回结果，包含模板ID和是否默认
            result['experiment']['template_id'] = result['experiment']['id']
        return result

# 测试函数
def test_database_matcher():
    matcher = DatabaseExperimentMatcher()
    
    # 测试案例
    test_inputs = [
        '钠在空气中的变化',
        '过氧化钠与水反应',
        '配制100mL 1.00mol/L NaCl溶液',
        '铝与盐酸反应',
        '乙烯与溴的加成反应',
        '乙酸乙酯的制备'
    ]
    
    for test_input in test_inputs:
        result = matcher.find_most_similar_experiment(test_input)
        if result:
            print(f"输入: {test_input}")
            print(f"匹配: {result['experiment']['title']}")
            print(f"相似度: {result['similarity']:.4f}")
            print()
        else:
            print(f"输入: {test_input}")
            print("无匹配结果")
            print()

if __name__ == "__main__":
    test_database_matcher()