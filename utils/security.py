from passlib.hash import argon2

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.

    :param password: The plain text password to verify.
    :param hashed_password: The hashed password to verify against.
    :return: True if the password matches the hash, False otherwise.
    """
    try:
        return argon2.verify(password, hashed_password)
    except Exception as e:
        print(f"Security: Error verifying password: {e}")
        return False


def generate_hashed_password(password: str) -> str:
    """
    Generate a hashed password using Argon2.

    :param password: The plain text password to hash.
    :return: The hashed password.
    """
    try:
        return argon2.using(
            type="id",
            rounds=3,
            memory_cost=65540,
            parallelism=4,
            salt_size=32,
        ).hash(password)
    except Exception as e:
        print(f"Error generating hashed password: {e}")
        return ""

if __name__ == "__main__":
    plain_password = input("Enter a password to hash: ")
    hashed = generate_hashed_password(plain_password)
    print(f"Hashed Password: {hashed}")
