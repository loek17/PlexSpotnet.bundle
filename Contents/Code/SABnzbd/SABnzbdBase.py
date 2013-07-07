import Helper
from SabSettings import SabSettings


def start():
    check , message = Helper.check_connection()
    if check:
        return True
    else:
        Dict['warning'].append(message)
        return False