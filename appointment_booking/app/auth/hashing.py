from passlib.context import CryptContext

hash_pwd = CryptContext(schemes=['bcrypt'],deprecated='auto')

def hash_password(password:str):
    return hash_pwd.hash(password)

def verify_hash(password:str, db_password:str):
    return hash_pwd.verify(password,db_password)