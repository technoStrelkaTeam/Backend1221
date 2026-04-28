import bcrypt


def check_password(password: str, hash: str):
    return bcrypt.checkpw(password.encode(), hash.encode())


def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()