
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

SEMAPHORE_KEY          = "6546842384123584"
NAME                   = "SpotNet for Plex"
APP_PREFIX             = "/applications/Plex-spotnet-python"
ART                    = 'art-default.jpg'
ICON                   = 'icon-default.jpg'

QUEUE                  = {'warning':[]}

MAX_CONNECTIONS        = int(get("MAX_CONNECTIONS" , 3))

OKE                    = None
