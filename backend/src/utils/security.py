# The following code is a temporary implementation of the security functions.
# Should be replaced with a more secure implementation.

import bcrypt
import uuid

def hash_password(password: str) -> str:
    """
    Hash a password
    (Temporary implementation)
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a stored password
    (Temporary implementation)
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def generate_account_number(user_id: int, account_type: str, prefix="ADX") -> str:
    """
    Generate an account number
    (Temporary implementation)
    """
    user_id_string = str(user_id).zfill(4).upper()
    account_string = account_type[:4].zfill(4).upper()
    random_part = uuid.uuid4().hex[:8].upper()
    return f"{prefix}{user_id_string}{account_string}{random_part}"

if __name__ == "__main__":
    print(generate_account_number(88, "cash"))