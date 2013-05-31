import Settings
from Connection import Connection, ConnectError

Settings.load()

@route('%s/Update/Update_Spots' % Settings.APP_PREFIX)
def update_spots():
    if 'thread' not in Settings.QUEUE or not Settings.QUEUE['thread'].isAlive():
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
    con = Connection(Settings.POST_DB , True)
    Settings.QUEUE['thread'] = Thread.Create(con.update)

@route('%s/Update/Dummy' % Settings.APP_PREFIX)
def dummy():
    pass
