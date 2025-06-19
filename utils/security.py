import bcrypt

# Hash password using bcrypt
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()  # Generate a salt for bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)  # Hash the password with the salt
    return hashed.decode('utf-8')  # Return hashed password as string

# Verify if the password matches the hashed password
def verify_password(raw_password: str, hashed: str) -> bool:
    return bcrypt.checkpw(raw_password.encode('utf-8'), hashed.encode('utf-8'))

