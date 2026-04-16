#工具文件：密码哈希
from passlib.context import CryptContext

# 使用更兼容的哈希算法配置
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],  # 改用PBKDF2算法，避免bcrypt的兼容性问题
    deprecated="auto"
)

def get_password_hash(password):
    """生成一个新的密码"""
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """验证密码是否一致"""
    return pwd_context.verify(plain_password, hashed_password)


if __name__ == '__main__':
    print(get_password_hash('123456'))
    print(get_password_hash('abc123'))