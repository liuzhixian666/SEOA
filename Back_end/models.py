#数据库模型
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(8), unique=True, index=True, nullable=False)  # 8位唯一ID
    phone = Column(String(20), unique=True, index=True, nullable=False)  # 手机号长度限制
    password = Column(String(255), nullable=False)  # 密码哈希长度限制
    name = Column(String(50), default="")  # 用户名长度限制
    user_type = Column(String(20), default="student")  # 用户类型：student 或 teacher
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), default="新对话")  # 对话标题长度限制
    user_id = Column(String(20), ForeignKey("users.phone"), nullable=False)  # 外键长度与主键一致
    summary_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)  # 消息内容，使用Text类型存储长文本
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class ExperimentEvaluation(Base):
    __tablename__ = "experiment_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, unique=True, nullable=False)  # 实验唯一ID
    title = Column(String(255), nullable=False)  # 实验标题
    content = Column(Text, nullable=False)  # 评价表内容，使用Text类型存储长文本
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(100), nullable=False)  # 班级名称
    class_code = Column(String(20), unique=True, nullable=False)  # 班级号，唯一
    description = Column(String(500), default="")  # 班级简介
    teacher_id = Column(String(20), ForeignKey("users.phone"), nullable=False)  # 班主任ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    teacher = relationship("User", foreign_keys=[teacher_id])
    members = relationship("ClassMember", back_populates="class_", cascade="all, delete-orphan")

class ClassMember(Base):
    __tablename__ = "class_members"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)  # 班级ID
    student_id = Column(String(20), ForeignKey("users.phone"), nullable=False)  # 学生ID
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    class_ = relationship("Class", back_populates="members")
    student = relationship("User", foreign_keys=[student_id])

class EvaluationTemplate(Base):
    __tablename__ = "evaluation_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(255), nullable=False)  # 模板名称
    description = Column(String(500), default="")  # 模板描述
    creator_id = Column(String(20), ForeignKey("users.phone"), nullable=False)  # 创建者ID
    is_default = Column(Boolean, default=False)  # 是否系统默认模板
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = relationship("User", foreign_keys=[creator_id])
    steps = relationship("TemplateStep", back_populates="template", cascade="all, delete-orphan")

class TemplateStep(Base):
    __tablename__ = "template_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("evaluation_templates.id"), nullable=False)  # 所属模板
    step_name = Column(String(255), nullable=False)  # 步骤名称
    step_order = Column(Integer, nullable=False)  # 步骤顺序
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    template = relationship("EvaluationTemplate", back_populates="steps")
    score_points = relationship("TemplateScorePoint", back_populates="step", cascade="all, delete-orphan")

class TemplateScorePoint(Base):
    __tablename__ = "template_score_points"
    
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(Integer, ForeignKey("template_steps.id"), nullable=False)  # 所属步骤
    point_name = Column(String(255), nullable=False)  # 评分点名称
    point_order = Column(Integer, nullable=False)  # 评分点顺序
    score = Column(Integer, nullable=False)  # 分值
    scoring_criteria = Column(Text, nullable=True)  # 评分标准
    deduction_description = Column(Text, nullable=False)  # 扣分点说明
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    step = relationship("TemplateStep", back_populates="score_points")

class Exam(Base):
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String(100), nullable=False)  # 考试名称
    description = Column(String(500), default="")  # 考试描述
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)  # 所属班级
    teacher_id = Column(String(20), ForeignKey("users.phone"), nullable=False)  # 发布教师
    template_id = Column(Integer, ForeignKey("evaluation_templates.id"), nullable=True)  # 评价表模板
    start_time = Column(DateTime, nullable=True)  # 开始时间
    end_time = Column(DateTime, nullable=True)  # 结束时间
    status = Column(String(20), default="published")  # 状态：published, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    class_ = relationship("Class")
    teacher = relationship("User", foreign_keys=[teacher_id])
    template = relationship("EvaluationTemplate")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    sender_id = Column(String(20), ForeignKey("users.phone"), nullable=False)
    receiver_id = Column(String(20), ForeignKey("users.phone"), nullable=False)
    related_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
