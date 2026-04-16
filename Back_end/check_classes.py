from database import SessionLocal
from models import Class

db = SessionLocal()
try:
    classes = db.query(Class).all()
    print('班级列表:')
    for cls in classes:
        print(f'ID: {cls.id}, 名称: {cls.class_name}, 教师ID: {cls.teacher_id}')
finally:
    db.close()