from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encrypt(password: str):
    return pwd_cxt.encrypt(password)

def verify(hashed_password, plain_password):
    return pwd_cxt.verify(plain_password, hashed_password)