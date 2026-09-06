import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password_input, database_password):
    if hash_password(password_input) == database_password:
        return True
    else:
        return False
