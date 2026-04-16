#登录业务
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User
from password_hash import verify_password, get_password_hash
from datetime import datetime, timedelta
from jose import jwt, JWTError

# JWT配置
SECRET_KEY = "my-secret-key123456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30分钟过期

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/ceea/login")

# 登录请求模型
class LoginRequest(BaseModel):
    username: str
    password: str

# 注册请求模型
class RegisterRequest(BaseModel):
    user_phone: str
    password: str

# 创建access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 获取当前用户
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_phone: str = payload.get("sub")
        if user_phone is None:
            raise credentials_exception
        # 检查token是否过期
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp")):
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.phone == user_phone).first()
    if user is None:
        raise credentials_exception
    
    return user

# 生成8位唯一用户ID
def generate_unique_user_id(db: Session) -> str:
    # 查询当前最大的user_id
    max_user = db.query(User).order_by(User.user_id.desc()).first()
    
    if not max_user:
        # 没有用户，从00000001开始
        next_id = 1
    else:
        # 有用户，在最大ID的基础上加1
        try:
            current_max_id = int(max_user.user_id)
            next_id = current_max_id + 1
        except ValueError:
            # 如果存在非数字的ID，从1开始
            next_id = 1
    
    # 确保生成的是8位数字，不足的前面补0
    user_id = f"{next_id:08d}"
    
    # 检查是否为00000000，如果是则加1
    if user_id == "00000000":
        user_id = "00000001"
    
    # 检查ID是否已存在（防止并发情况下的冲突）
    existing_user = db.query(User).filter(User.user_id == user_id).first()
    if existing_user:
        # 如果存在，递归调用生成下一个ID
        return generate_unique_user_id(db)
    
    return user_id

# 注册接口
def register_router(app: FastAPI):
    @app.post("/api/ceea/register")
    def register(request: RegisterRequest, db: Session = Depends(get_db)):
        user_phone = request.user_phone
        password = request.password
        
        # 检查电话号码是否已被注册
        existing_user = db.query(User).filter(User.phone == user_phone).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="该电话号码已被注册")
        
        # 生成唯一的8位用户ID
        user_id = generate_unique_user_id(db)
        
        # 对密码进行哈希处理
        hashed_password = get_password_hash(password)
        
        # 创建新用户
        new_user = User(
            user_id=user_id,
            phone=user_phone,
            password=hashed_password,
            name=""
        )
        
        # 保存到数据库
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "message": "注册成功",
            "user_id": new_user.user_id,
            "user_phone": new_user.phone,
            "name": new_user.name
        }

    @app.post("/api/ceea/login")
    def login(request: LoginRequest, db: Session = Depends(get_db)):
        user_phone = request.username
        password = request.password
        
        user = db.query(User).filter(User.phone == user_phone).first()
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="账号或密码错误")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.phone},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.user_id,
            "user_type": user.user_type
        }

    @app.get("/api/ceea/users/me")
    def get_me(current_user: User = Depends(get_current_user)):
        return {
            "user_id": current_user.user_id,
            "user_phone": current_user.phone,
            "name": current_user.name,
            "user_type": current_user.user_type,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at
        }
