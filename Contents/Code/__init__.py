#####################################################################
#
# File:        __init__.py
# Author:   Loek Wensveen
# Date:      14/09/2012
# Version: 0.1
# About:        Spotnet plugin for plex
#
#####################################################################
import sys
sys.path.append(Core.storage.join_path(Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name) , 'Plex-spotnet-python.bundle' , 'Contents' , "Code"))

import Base_Settings
from Spotnet import Edit_Filter , Search , Update , BaseSpotnet
from SABnzbd import SABnzbdBase

"""
view_modes = {
  "List": 65586, "InfoList": 65592, "MediaPreview": 458803, "Showcase": 458810, "Coverflow": 65591, 
  "PanelStream": 131124, "WallStream": 131125, "Songs": 65593, "Seasons": 65593, "Albums": 131123, 
  "Episodes": 65590,"ImageStream":458809,"Pictures":131123
}
  def add_view_group(self, name, viewMode=None, mediaType=None, type=None, menu=None, cols=None, rows=None, thumb=None, summary=None)
"""

def Start():
    # Initialize the plugin
    Plugin.AddPrefixHandler(Base_Settings.APP_PREFIX, MainMenu, Base_Settings.NAME, Base_Settings.ICON, Base_Settings.ART)
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("InfoList", viewMode = "InfoList", mediaType = "items")
    Plugin.AddViewGroup("MediaPreview", viewMode="MediaPreview", mediaType="items")
    Plugin.AddViewGroup("Showcase", viewMode="Showcase", mediaType="items")
    Plugin.AddViewGroup("Coverflow", viewMode="Coverflow", mediaType="items")
    Plugin.AddViewGroup("PanelStream", viewMode="PanelStream", mediaType="items")
    Plugin.AddViewGroup("WallStream", viewMode="WallStream", mediaType="items")
    Plugin.AddViewGroup("Songs", viewMode="Songs", mediaType="items")
    Plugin.AddViewGroup("Seasons", viewMode="Seasons", mediaType="items")
    Plugin.AddViewGroup("Albums", viewMode="Albums", mediaType="items")
    Plugin.AddViewGroup('Episode', viewMode='Episodes', mediaType='items')
    Plugin.AddViewGroup("ImageStream", viewMode="ImageStream", mediaType="items")
    Plugin.AddViewGroup("Pictures", viewMode="Pictures", mediaType="items")
    
    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1 = Base_Settings.NAME
    ObjectContainer.view_group = 'MediaPreview'
    ObjectContainer.art = R(Base_Settings.ART)
    
    CheckPrefs()
    
    
def CheckPrefs(retry=False):
    if BaseSpotnet.start() and SABnzbdBase.start():
        Base_Settings.OKE = True
    else:
        Base_Settings.QUEUE['warning'].insert(0,'Not all settings are set correct!')
        Base_Settings.OKE = False 
    
    if retry:
        return MainMenu()


@route("%s/MainMenu" % Base_Settings.APP_PREFIX)
def MainMenu():
    if Base_Settings.OKE:
        oc = ObjectContainer(
            replace_parent = True,
            objects = [
                DirectoryObject(
                    key = Callback(test),
                    title = "test func"
                ),
                DirectoryObject(
                    key = Callback(Categories),
                    title = "Categories"
                ),
                PopupDirectoryObject(
                    key = Callback(Zoeken),
                    title = "Zoeken"
                ),
                PopupDirectoryObject(
                    key = Callback(EditFilters),
                    title = "Edit Filters"
                ),
                PopupDirectoryObject(
                    key = Callback(UpdateFunc),
                    title = "Update Database",
                    summary = "Update your spot database, this may take al well"
                ),
                PrefsObject(title='Preferences')
            ]
        )
    else:
        oc = ObjectContainer(
            replace_parent = True,
            objects=[
                DirectoryObject(
                    key = Callback(CheckPrefs , retry=True),
                    title = "Warning not al settings are set correct",
                    summary = '\n'.join(Base_Settings.QUEUE['warning'])
                ),
                PrefsObject(title='Preferences')
            ]
        )
    return oc
    
def Categories():
    return BaseSpotnet.display_categories()
    
def Zoeken():
    return Search.display_categories()

def EditFilters():
    return Edit_Filter.display_categories()
    
def UpdateFunc():
    return Update.update_spots()

def test():
    image = R("art-default.jpg")
    Log.Info(image)
