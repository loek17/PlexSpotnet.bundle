import Api
import SabSettings
#from Spotnet.Connection import Connection

class ConException(Exception):
    pass

def add_spotnet_post(post , **kwargs):   
    if post.has_encrypted_nzbsite():
        resp = Api.add_url(get_encrypted_nzbsite() , post.title , **kwargs)
    elif post.has_nzb():
        resp = Api.add_file(post.get_nzb_content() , post.title , **kwargs)
    return resp

def check_connection():
    try:
        resp = Api.version()
    except ConException as e:
        Log.Info(e)
        return False , e
    if "Error" in resp:
        return False , resp['Error']
    return True , "oke"

def remove_connection():
    pass

