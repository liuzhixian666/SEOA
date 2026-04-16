#评价表模板管理
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User, EvaluationTemplate, TemplateStep, TemplateScorePoint
from auth import get_current_user

# 评价表模板相关请求模型
class CreateTemplateRequest(BaseModel):
    template_name: str
    description: str = ""

class CreateTemplateStepRequest(BaseModel):
    step_name: str
    step_order: int

class CreateTemplateScorePointRequest(BaseModel):
    point_name: str
    point_order: int
    score: int
    deduction_description: str

# 评价表模板相关接口
def register_router(app: FastAPI):
    # 获取评价表模板列表
    @app.get("/api/ceea/templates")
    def get_templates(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为教师
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以查看评价表模板")
        
        # 获取所有模板（系统默认和用户创建的）
        templates = db.query(EvaluationTemplate).all()
        
        return [{
            "id": template.id,
            "template_name": template.template_name,
            "description": template.description,
            "is_default": template.is_default,
            "created_at": template.created_at
        } for template in templates]

    # 创建评价表模板
    @app.post("/api/ceea/templates")
    def create_template(request: CreateTemplateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为教师
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以创建评价表模板")
        
        # 创建模板
        new_template = EvaluationTemplate(
            template_name=request.template_name,
            description=request.description,
            creator_id=current_user.phone,
            is_default=False
        )
        db.add(new_template)
        db.commit()
        db.refresh(new_template)
        
        return {
            "id": new_template.id,
            "template_name": new_template.template_name,
            "description": new_template.description,
            "created_at": new_template.created_at
        }

    # 获取评价表模板详情
    @app.get("/api/ceea/templates/{template_id}")
    def get_template_detail(template_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为教师
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以查看评价表模板详情")
        
        # 查找模板
        template = db.query(EvaluationTemplate).filter(EvaluationTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="评价表模板不存在")
        
        # 构建模板详情
        steps = []
        for step in sorted(template.steps, key=lambda x: x.step_order):
            score_points = []
            for point in sorted(step.score_points, key=lambda x: x.point_order):
                score_points.append({
                    "id": point.id,
                    "point_name": point.point_name,
                    "point_order": point.point_order,
                    "score": point.score,
                    "deduction_description": point.deduction_description
                })
            steps.append({
                "id": step.id,
                "step_name": step.step_name,
                "step_order": step.step_order,
                "score_points": score_points
            })
        
        return {
            "id": template.id,
            "template_name": template.template_name,
            "description": template.description,
            "is_default": template.is_default,
            "created_at": template.created_at,
            "steps": steps
        }

    # 添加模板步骤
    @app.post("/api/ceea/templates/{template_id}/steps")
    def add_template_step(template_id: int, request: CreateTemplateStepRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为教师
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以修改评价表模板")
        
        # 查找模板
        template = db.query(EvaluationTemplate).filter(EvaluationTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="评价表模板不存在")
        
        # 检查是否为模板创建者
        if template.creator_id != current_user.phone and not template.is_default:
            raise HTTPException(status_code=403, detail="无权修改该评价表模板")
        
        # 创建步骤
        new_step = TemplateStep(
            template_id=template_id,
            step_name=request.step_name,
            step_order=request.step_order
        )
        db.add(new_step)
        db.commit()
        db.refresh(new_step)
        
        return {
            "id": new_step.id,
            "step_name": new_step.step_name,
            "step_order": new_step.step_order,
            "created_at": new_step.created_at
        }

    # 添加模板步骤的评分点
    @app.post("/api/ceea/templates/steps/{step_id}/score-points")
    def add_template_score_point(step_id: int, request: CreateTemplateScorePointRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为教师
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以修改评价表模板")
        
        # 查找步骤
        step = db.query(TemplateStep).filter(TemplateStep.id == step_id).first()
        if not step:
            raise HTTPException(status_code=404, detail="步骤不存在")
        
        # 查找模板
        template = db.query(EvaluationTemplate).filter(EvaluationTemplate.id == step.template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="评价表模板不存在")
        
        # 检查是否为模板创建者
        if template.creator_id != current_user.phone and not template.is_default:
            raise HTTPException(status_code=403, detail="无权修改该评价表模板")
        
        # 创建评分点
        new_score_point = TemplateScorePoint(
            step_id=step_id,
            point_name=request.point_name,
            point_order=request.point_order,
            score=request.score,
            deduction_description=request.deduction_description
        )
        db.add(new_score_point)
        db.commit()
        db.refresh(new_score_point)
        
        return {
            "id": new_score_point.id,
            "point_name": new_score_point.point_name,
            "point_order": new_score_point.point_order,
            "score": new_score_point.score,
            "deduction_description": new_score_point.deduction_description,
            "created_at": new_score_point.created_at
        }

    # 删除评价表模板
    @app.delete("/api/ceea/templates/{template_id}")
    def delete_template(template_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为教师
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以删除评价表模板")
        
        # 查找模板
        template = db.query(EvaluationTemplate).filter(EvaluationTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="评价表模板不存在")
        
        # 检查是否为模板创建者
        if template.creator_id != current_user.phone:
            raise HTTPException(status_code=403, detail="无权删除该评价表模板")
        
        # 检查是否为系统默认模板
        if template.is_default:
            raise HTTPException(status_code=403, detail="系统默认模板不能删除")
        
        # 删除模板
        db.delete(template)
        db.commit()
        
        return {"message": "评价表模板已成功删除"}
