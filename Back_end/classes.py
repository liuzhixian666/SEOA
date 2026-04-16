#班级管理
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User, Class, ClassMember
from auth import get_current_user
import random
import string

# 班级相关请求模型
class CreateClassRequest(BaseModel):
    class_name: str
    description: str = ""

class JoinClassRequest(BaseModel):
    class_code: str

class AddStudentRequest(BaseModel):
    student_id: str

# 生成随机班级号
def generate_class_code(length=8):
    letters_and_digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

# 班级管理接口
def register_router(app: FastAPI):
    # 创建班级（教师）
    @app.post("/api/ceea/classes")
    def create_class(request: CreateClassRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为教师
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以创建班级")
        
        # 生成唯一班级号
        class_code = generate_class_code()
        while db.query(Class).filter(Class.class_code == class_code).first():
            class_code = generate_class_code()
        
        # 创建班级
        new_class = Class(
            class_name=request.class_name,
            class_code=class_code,
            description=request.description,
            teacher_id=current_user.phone
        )
        db.add(new_class)
        db.commit()
        db.refresh(new_class)
        
        return {
            "id": new_class.id,
            "class_name": new_class.class_name,
            "class_code": new_class.class_code,
            "teacher_id": new_class.teacher_id,
            "created_at": new_class.created_at
        }

    # 获取教师的班级列表
    @app.get("/api/ceea/classes")
    def get_teacher_classes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为教师
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以查看班级列表")
        
        classes = db.query(Class).filter(Class.teacher_id == current_user.phone).all()
        
        return [{
            "id": cls.id,
            "class_name": cls.class_name,
            "class_code": cls.class_code,
            "description": cls.description,
            "created_at": cls.created_at
        } for cls in classes]

    # 加入班级（学生）
    @app.post("/api/ceea/classes/join")
    def join_class(request: JoinClassRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为学生
        if current_user.user_type != "student":
            raise HTTPException(status_code=403, detail="只有学生可以加入班级")
        
        # 查找班级
        class_ = db.query(Class).filter(Class.class_code == request.class_code).first()
        if not class_:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        # 检查是否已加入
        existing_member = db.query(ClassMember).filter(
            ClassMember.class_id == class_.id,
            ClassMember.student_id == current_user.phone
        ).first()
        if existing_member:
            raise HTTPException(status_code=400, detail="已加入该班级")
        
        # 加入班级
        new_member = ClassMember(
            class_id=class_.id,
            student_id=current_user.phone
        )
        db.add(new_member)
        db.commit()
        
        return {
            "message": "加入班级成功",
            "class_id": class_.id,
            "class_name": class_.class_name
        }

    # 获取学生的班级列表
    @app.get("/api/ceea/student/classes")
    def get_student_classes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 检查是否为学生
        if current_user.user_type != "student":
            raise HTTPException(status_code=403, detail="只有学生可以查看班级列表")
        
        # 获取学生加入的班级
        members = db.query(ClassMember).filter(ClassMember.student_id == current_user.phone).all()
        classes = []
        for member in members:
            class_ = member.class_
            classes.append({
                "id": class_.id,
                "class_name": class_.class_name,
                "class_code": class_.class_code,
                "teacher_id": class_.teacher_id,
                "joined_at": member.joined_at
            })
        
        return classes

    # 获取班级详情
    @app.get("/api/ceea/classes/{class_id}")
    def get_class_detail(class_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 查找班级
        class_ = db.query(Class).filter(Class.id == class_id).first()
        if not class_:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        # 检查权限（教师或班级成员）
        if current_user.user_type == "teacher":
            if class_.teacher_id != current_user.phone:
                raise HTTPException(status_code=403, detail="无权访问该班级")
        else:
            # 学生需要是班级成员
            member = db.query(ClassMember).filter(
                ClassMember.class_id == class_id,
                ClassMember.student_id == current_user.phone
            ).first()
            if not member:
                raise HTTPException(status_code=403, detail="无权访问该班级")
        
        # 获取班级成员
        members = db.query(ClassMember).filter(ClassMember.class_id == class_id).all()
        member_list = []
        for member in members:
            student = db.query(User).filter(User.phone == member.student_id).first()
            member_list.append({
                "student_id": student.user_id if student else member.student_id,
                "student_name": student.name if student else "",
                "joined_at": member.joined_at
            })
        
        return {
            "id": class_.id,
            "class_name": class_.class_name,
            "class_code": class_.class_code,
            "description": class_.description,
            "teacher_id": class_.teacher_id,
            "created_at": class_.created_at,
            "members": member_list
        }

    # 教师添加学生到班级
    @app.post("/api/ceea/classes/{class_id}/students")
    def add_student_to_class(class_id: int, request: AddStudentRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以添加学生")
        
        class_ = db.query(Class).filter(Class.id == class_id).first()
        if not class_:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        if class_.teacher_id != current_user.phone:
            raise HTTPException(status_code=403, detail="无权操作该班级")
        
        student = db.query(User).filter(User.user_id == request.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
        
        if student.user_type != "student":
            raise HTTPException(status_code=400, detail="该用户不是学生")
        
        existing_member = db.query(ClassMember).filter(
            ClassMember.class_id == class_id,
            ClassMember.student_id == student.phone
        ).first()
        if existing_member:
            raise HTTPException(status_code=400, detail="该学生已在班级中")
        
        new_member = ClassMember(
            class_id=class_id,
            student_id=student.phone
        )
        db.add(new_member)
        db.commit()
        
        return {
            "message": "添加学生成功",
            "class_id": class_id,
            "student_id": student.user_id,
            "student_name": student.name
        }

    # 教师从班级中移除学生
    @app.delete("/api/ceea/classes/{class_id}/students/{student_id}")
    def remove_student_from_class(class_id: int, student_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        if current_user.user_type != "teacher":
            raise HTTPException(status_code=403, detail="只有教师可以移除学生")
        
        class_ = db.query(Class).filter(Class.id == class_id).first()
        if not class_:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        if class_.teacher_id != current_user.phone:
            raise HTTPException(status_code=403, detail="无权操作该班级")
        
        student = db.query(User).filter(User.user_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
        
        class_member = db.query(ClassMember).filter(
            ClassMember.class_id == class_id,
            ClassMember.student_id == student.phone
        ).first()
        if not class_member:
            raise HTTPException(status_code=400, detail="该学生不在此班级中")
        
        db.delete(class_member)
        db.commit()
        
        return {
            "message": "移除学生成功",
            "class_id": class_id,
            "student_id": student.user_id,
            "student_name": student.name
        }

    # 解散班级（教师）
    @app.delete("/api/ceea/classes/{class_id}")
    def delete_class(class_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 查找班级
        class_ = db.query(Class).filter(Class.id == class_id).first()
        if not class_:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        if class_.teacher_id != current_user.phone:
            raise HTTPException(status_code=403, detail="无权解散该班级")
        
        # 删除班级（由于class_members表设置了ON DELETE CASCADE，所以班级的所有成员记录会自动删除）
        db.delete(class_)
        db.commit()
        
        return {"message": "班级已成功解散"}
