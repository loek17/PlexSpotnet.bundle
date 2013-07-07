from SpotnetSettings import SpotSettings as Settings
from Connection import Connection

UpdateThread = None

@route('%s/Update/Update_Spots' % Settings.APP_PREFIX)
def update_spots():
    if not UpdateThread or not UpdateThread.isAlive():
        oc = ObjectContainer(
            objects = [
                DirectoryObject(
                    key = Callback(start_update),
                    title = "Update Spots"
                ),
                DirectoryObject(
                    key = Callback(dummy),
                    title = "Exit"
                )
            ]
        )
    else:
        oc = ObjectContainer(
            objects = [
                DirectoryObject(
                    key = Callback(dummy),
                    title = "Already updating"
                ),
                DirectoryObject(
                    key = Callback(dummy),
                    title = "Exit"
                )
            ]
        )
    return oc

@route('%s/Update/Start_Update' % Settings.APP_PREFIX)
def start_update():
    global UpdateThread
    if not UpdateThread or not UpdateThread.isAlive():
        con = Connection(Settings.POST_DB , True)
        UpdateThread = Thread.Create(con.update)
    else:
        Thread.CreateTimer(86400.0 , con.update)
    

@route('%s/Update/Dummy' % Settings.APP_PREFIX)
def dummy():
    pass
