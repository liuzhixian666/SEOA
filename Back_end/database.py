#数据库配置
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from password_hash import get_password_hash

# MySQL数据库配置 - 请根据您的实际MySQL配置修改以下参数
DB_USER = "root"           # MySQL用户名，通常为root
DB_PASSWORD = "lzx200606"          # MySQL密码，请输入您的实际密码
DB_HOST = "localhost"     # MySQL主机地址，通常为localhost
DB_PORT = 3306            # MySQL端口，默认3306
DB_NAME = "ceea"          # 数据库名称，已创建的ceea数据库

# 数据库URL - MySQL
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库
def init_db():
    # 导入所有模型以确保它们被SQLAlchemy识别
    try:
        from .models import User, Conversation, Message, ExperimentEvaluation, Class, ClassMember, Exam, EvaluationTemplate, TemplateStep, TemplateScorePoint, Notification
    except ImportError:
        # 如果相对导入失败，尝试绝对导入
        from models import User, Conversation, Message, ExperimentEvaluation, Class, ClassMember, Exam, EvaluationTemplate, TemplateStep, TemplateScorePoint, Notification
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"\n=== 数据库初始化错误 ===")
        print(f"错误信息: {e}")
        raise
    
    # 如添加默认用户（果不存在）
    db = SessionLocal()
    try:
        # 检查是否已有默认学生用户
        existing_student_user = db.query(User).filter(User.phone == "13800138000").first()
        if not existing_student_user:
            # 生成唯一的8位用户ID（按顺序）
            max_user = db.query(User).order_by(User.user_id.desc()).first()
            if not max_user:
                user_id = "00000001"
            else:
                try:
                    current_max_id = int(max_user.user_id)
                    next_id = current_max_id + 1
                    user_id = f"{next_id:08d}"
                except ValueError:
                    user_id = "00000001"
            # 检查是否为00000000，如果是则使用00000001
            if user_id == "00000000":
                user_id = "00000001"
            # 检查ID是否已存在
            existing_id = db.query(User).filter(User.user_id == user_id).first()
            if existing_id:
                # 如果存在，重新生成
                max_user = db.query(User).order_by(User.user_id.desc()).first()
                if max_user:
                    try:
                        current_max_id = int(max_user.user_id)
                        next_id = current_max_id + 1
                        user_id = f"{next_id:08d}"
                    except ValueError:
                        user_id = "00000001"
                else:
                    user_id = "00000001"
            # 创建默认用户
            default_student_user = User(
                user_id=user_id,
                phone="13800138000",
                password=get_password_hash("test123"),
                user_type="student",
                name="Test Student User"
            )
            db.add(default_student_user)
            db.commit()

        # 检查是否已有教师默认用户
        existing_teacher_user = db.query(User).filter(User.phone == "13900139000").first()
        if not existing_teacher_user:
            # 生成唯一的8位用户ID（按顺序）
            max_user = db.query(User).order_by(User.user_id.desc()).first()
            if not max_user:
                user_id = "00000002"
            else:
                try:
                    current_max_id = int(max_user.user_id)
                    next_id = current_max_id + 1
                    user_id = f"{next_id:08d}"
                except ValueError:
                    user_id = "00000002"
            # 检查是否为00000000，如果是则使用00000002
            if user_id == "00000000":
                user_id = "00000002"
            # 检查ID是否已存在
            existing_id = db.query(User).filter(User.user_id == user_id).first()
            if existing_id:
                # 如果存在，重新生成
                max_user = db.query(User).order_by(User.user_id.desc()).first()
                if max_user:
                    try:
                        current_max_id = int(max_user.user_id)
                        next_id = current_max_id + 1
                        user_id = f"{next_id:08d}"
                    except ValueError:
                        user_id = "00000002"
                else:
                    user_id = "00000002"
            # 创建默认用户
            default_teacher_user = User(
                user_id=user_id,
                phone="13900139000",
                password=get_password_hash("teacher123"),
                user_type = "teacher",
                name="Test Teacher User"
            )
            db.add(default_teacher_user)
            db.commit()
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        db.rollback()
    finally:
        db.close()
