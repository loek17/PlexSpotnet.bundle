from BaseSettings import Settings

def _(str):
    try:
        str = L(str)
    except:
        pass
    return str

def get(name , fallback):
    try:
        retr = Prefs[name]
    except:
        retr = fallback
    return retr

class SabSettings(Settings):
    SABNZBD_IP = get("SABNZBD_IP" , "127.0.0.1")
    SABNZBD_POORT = get("SABNZBD_POORT" , "8080")
    SABNZBD_HTTPS = get("SABNZBD_HTTPS" , False)
    SABNZBD_MODE = "json"
    SABUSER = get("SABNZBD_USER" , "")
    SABPASS = get("SABNZBD_PASS" , "")
