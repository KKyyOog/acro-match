from datetime import datetime

def is_valid_birthday_yyyymmdd(birthday: str) -> bool:
    """
    Checks if birthday string is a valid date in YYYYMMDD format.
    """
    if len(birthday) != 8 or not birthday.isdigit():
        return False
    try:
        datetime.strptime(birthday, "%Y%m%d")
        return True
    except ValueError:
        return False