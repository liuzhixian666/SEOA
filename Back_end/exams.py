#考试管理
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User, Class, Exam
from auth import get_current_user
from datetime import datetime

# 考试相关请求模型
class CreateExamRequest(BaseModel):
    exam_name: str
    description: str = ""
    class_id: int
    template_id: int = None
    start_time: str = None
    end_time: str = None

class UpdateExamRequest(BaseModel):
    exam_name: str
    description: str = ""
    class_id: int
    template_id: int = None
    start_time: str = None
    end_time: str = None

# 考试系统接口
def register_router(app: FastAPI):
    # 创建考试（教师）
    @app.post("/api/ceea/exams")
    def create_exam(request: CreateExamRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        try:
            # 检查是否为教师
            if current_user.user_type != "teacher":
                raise HTTPException(status_code=403, detail="只有教师可以发布考试")
            
            # 检查班级是否存在且属于该教师
            class_ = db.query(Class).filter(Class.id == request.class_id).first()
            if not class_:
                raise HTTPException(status_code=404, detail="班级不存在")
            if class_.teacher_id != current_user.phone:
                raise HTTPException(status_code=403, detail="无权为该班级发布考试")
            
            # 检查评价表模板是否存在
            if request.template_id:
                from models import EvaluationTemplate
                template = db.query(EvaluationTemplate).filter(EvaluationTemplate.id == request.template_id).first()
                if not template:
                    raise HTTPException(status_code=404, detail="评价表模板不存在")
            
            # 处理时间格式
            start_time = None
            end_time = None
            if request.start_time:
                try:
                    # 处理前端datetime-local格式，如"2023-12-31T23:59"
                    start_time = datetime.fromisoformat(request.start_time)
                except Exception as e:
                    print(f"解析开始时间失败: {e}")
                    pass
            if request.end_time:
                try:
                    # 处理前端datetime-local格式，如"2023-12-31T23:59"
                    end_time = datetime.fromisoformat(request.end_time)
                except Exception as e:
                    print(f"解析结束时间失败: {e}")
                    pass
            
            # 创建考试
            new_exam = Exam(
                exam_name=request.exam_name,
                description=request.description,
                class_id=request.class_id,
                teacher_id=current_user.phone,
                template_id=request.template_id,
                start_time=start_time,
                end_time=end_time,
                status="published"
            )
            db.add(new_exam)
            db.commit()
            db.refresh(new_exam)

            # 自动向班级学生发送考试通知
            try:
                from models import Notification, ClassMember
                from datetime import datetime

                # 查询班级所有学生成员
                students = db.query(ClassMember).filter(
                    ClassMember.class_id == request.class_id
                ).all()

                # 格式化时间显示
                start_time_str = start_time.strftime("%Y-%m-%d %H:%M") if start_time else "待定"
                end_time_str = end_time.strftime("%Y-%m-%d %H:%M") if end_time else "待定"

                # 为每个学生创建通知
                for student in students:
                    notification = Notification(
                        title=f"新考试：{request.exam_name}",
                        content=(
                            f"{current_user.name or current_user.phone}老师"
                            f"发布了新考试《{request.exam_name}》\n"
                            f"开始时间：{start_time_str}\n"
                            f"结束时间：{end_time_str}"
                        ),
                        notification_type="exam_announcement",
                        sender_id=current_user.phone,
                        receiver_id=student.student_id,
                        related_id=new_exam.id
                    )
                    db.add(notification)

                db.commit()
            except Exception as notify_error:
                print(f"发送考试通知失败（不影响考试创建）: {notify_error}")
                # 通知失败不影响主流程

            return {
                "id": new_exam.id,
                "exam_name": new_exam.exam_name,
                "description": new_exam.description,
                "class_id": new_exam.class_id,
                "class_name": class_.class_name,
                "teacher_id": new_exam.teacher_id,
                "template_id": new_exam.template_id,
                "start_time": new_exam.start_time,
                "end_time": new_exam.end_time,
                "status": new_exam.status,
                "created_at": new_exam.created_at
            }
        except Exception as e:
            print(f"创建考试失败: {e}")
            raise HTTPException(status_code=500, detail=f"创建考试失败: {str(e)}")

    # 获取教师的考试列表
    @app.get("/api/ceea/exams")
    def get_teacher_exams(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为教师
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以查看考试列表")
        
        # 获取教师发布的所有考试
        exams = db.query(Exam).filter(Exam.teacher_id == current_user.phone).all()
        
        exam_list = []
        for exam in exams:
            class_ = db.query(Class).filter(Class.id == exam.class_id).first()
            class_name = class_.class_name if class_ else "未知班级"
            
            exam_list.append({
                "id": exam.id,
                "exam_name": exam.exam_name,
                "description": exam.description,
                "class_id": exam.class_id,
                "class_name": class_name,
                "teacher_id": exam.teacher_id,
                "start_time": exam.start_time,
                "end_time": exam.end_time,
                "status": exam.status,
                "created_at": exam.created_at
            })
        
        return exam_list


    # 删除考试
    @app.delete("/api/ceea/exams/{exam_id}")
    def delete_exam(exam_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 查找考试
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="考试不存在")
        
        # 检查权限（只有发布该考试的教师可以删除）
        if exam.teacher_id != current_user.phone:
            raise HTTPException(status_code=403, detail="无权删除该考试")
        
        # 删除考试
        db.delete(exam)
        db.commit()
        
        return {"message": "考试已成功删除"}
    
    # 更新考试（教师）
    @app.put("/api/ceea/exams/{exam_id}")
    def update_exam(exam_id: int, request: UpdateExamRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为教师
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以更新考试")
        
        # 查找考试
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="考试不存在")
        
       
        if exam.teacher_id != current_user.phone:
            raise HTTPException(status_code=403, detail="无权更新该考试")
        
        # 检查班级是否存在且属于该教师
        class_ = db.query(Class).filter(Class.id == request.class_id).first()
        if not class_:
            raise HTTPException(status_code=404, detail="班级不存在")
        if class_.teacher_id != current_user.phone:
            raise HTTPException(status_code=403, detail="无权为该班级更新考试")
        
        # 检查评价表模板是否存在
        if request.template_id:
            from models import EvaluationTemplate
            template = db.query(EvaluationTemplate).filter(EvaluationTemplate.id == request.template_id).first()
            if not template:
                raise HTTPException(status_code=404, detail="评价表模板不存在")
        
        # 处理时间格式
        start_time = None
        end_time = None
        if request.start_time:
            try:
                
                start_time = datetime.fromisoformat(request.start_time)
            except Exception as e:
                print(f"解析开始时间失败: {e}")
                pass
        if request.end_time:
            try:
                end_time = datetime.fromisoformat(request.end_time)
            except Exception as e:
                print(f"解析结束时间失败: {e}")
                pass
        
        # 更新考试
        exam.exam_name = request.exam_name
        exam.description = request.description
        exam.class_id = request.class_id
        exam.template_id = request.template_id
        exam.start_time = start_time
        exam.end_time = end_time
        
        db.commit()
        db.refresh(exam)
        
        return {
            "id": exam.id,
            "exam_name": exam.exam_name,
            "description": exam.description,
            "class_id": exam.class_id,
            "class_name": class_.class_name,
            "teacher_id": exam.teacher_id,
            "template_id": exam.template_id,
            "start_time": exam.start_time,
            "end_time": exam.end_time,
            "status": exam.status,
            "created_at": exam.created_at,
            "updated_at": exam.updated_at
        }
    
    # 获取学生可参加的考试列表
    @app.get("/api/ceea/student/exams")
    def get_student_exams(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为学生
        if current_user.user_type != "student":
            raise HTTPException(status_code=403, detail="只有学生可以查看考试列表")
        
        # 获取学生所在的班级
        from models import ClassMember
        member_records = db.query(ClassMember).filter(ClassMember.student_id == current_user.phone).all()
        class_ids = [member.class_id for member in member_records]
        
        if not class_ids:
            return []
        
        # 获取这些班级的考试
        exams = db.query(Exam).filter(Exam.class_id.in_(class_ids)).all()
        
        exam_list = []
        for exam in exams:
            class_ = db.query(Class).filter(Class.id == exam.class_id).first()
            class_name = class_.class_name if class_ else "未知班级"
            
            exam_list.append({
                "id": exam.id,
                "exam_name": exam.exam_name,
                "description": exam.description,
                "class_id": exam.class_id,
                "class_name": class_name,
                "teacher_id": exam.teacher_id,
                "start_time": exam.start_time,
                "end_time": exam.end_time,
                "status": exam.status,
                "created_at": exam.created_at
            })
        
        return exam_list
    
    # 修改考试详情接口，允许学生查看
    @app.get("/api/ceea/exams/{exam_id}")
    def get_exam_detail(exam_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 查找考试
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="考试不存在")
        
        # 检查权限（教师或该考试班级的学生）
        if current_user.user_type == "teacher":
            if exam.teacher_id != current_user.phone:
                raise HTTPException(status_code=403, detail="无权访问该考试")
        else:
            # 学生需要是该考试班级的成员
            from models import ClassMember
            member = db.query(ClassMember).filter(
                ClassMember.class_id == exam.class_id,
                ClassMember.student_id == current_user.phone
            ).first()
            if not member:
                raise HTTPException(status_code=403, detail="无权访问该考试")
        
        # 获取班级信息
        class_ = db.query(Class).filter(Class.id == exam.class_id).first()
        class_name = class_.class_name if class_ else "未知班级"
        
        return {
            "id": exam.id,
            "exam_name": exam.exam_name,
            "description": exam.description,
            "class_id": exam.class_id,
            "class_name": class_name,
            "teacher_id": exam.teacher_id,
            "start_time": exam.start_time,
            "end_time": exam.end_time,
            "status": exam.status,
            "created_at": exam.created_at,
            "updated_at": exam.updated_at
        }
