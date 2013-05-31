import Helper
import SabSettings


def start():
    check , message = Helper.check_connection()
    if check:
        return True
    else:
        SabSettings.QUEUE['warning'].append(message)
        return False