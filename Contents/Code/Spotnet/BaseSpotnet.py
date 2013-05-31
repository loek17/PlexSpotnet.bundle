from Errors import *
from Filter import Filter
from Database import PostDatabase , FilterDatabase
from Connection import Connection

import Settings
#import Edit_Filter
import Update
import Search

import SABnzbd

###################################################
# the display functions of spotnet are in here
# 
#
#  Loek Wensveen
#
###################################################


def start():
    #TODO maby test internet and newsserver connection
    Settings.load()
    if Settings.UPDATE_ON_BOOT:
        Update.start_update()
    
    Settings.ROOT_PATH              = Core.storage.join_path(Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name) , 'Plex-spotnet-python.bundle' , 'Contents')
    Settings.IMAGE_DIR              = Core.storage.join_path(Settings.ROOT_PATH , 'Resources' , "%s.jpg")
    Settings.DB_DIR                 = Core.storage.join_path(Settings.ROOT_PATH , 'Database')
    Settings.POST_DB                = PostDatabase()
    Settings.FILTER_DB              = FilterDatabase()
    
    
    return True
    
@route('%s/BaseSpotnet/Display_Categories' % Settings.APP_PREFIX)    
def display_categories():
    oc = ObjectContainer(
        objects = [
            DirectoryObject(
                key = Callback(display_filters , cat=1),
                title = "Beeld"
            ),
            DirectoryObject(
                key = Callback(display_filters , cat=2),
                title = "Music"
            ),
            DirectoryObject(
                key = Callback(display_filters , cat=3),
                title = "Games"
            ),
            DirectoryObject(
                key = Callback(display_filters , cat=4),
                title = "Applications"
            )
        ]
    )
    return oc

@route('%s/BaseSpotnet/Display_Filters' % Settings.APP_PREFIX , cat=int)    
def display_filters(cat):
    filters = Settings.FILTER_DB.get_filters(cat)
    oc = ObjectContainer(
        objects = [
            InputDirectoryObject(
                key = Callback(search , cat=cat , advanced = False),
                title = "Zoeken in " + Settings.CATEGORY_MAPPING[cat]
            )
        ]
    )
    for filter in filters:
        oc.add(
            DirectoryObject(
                key = Callback(display_filter , filter = filter.id),
                title = filter.name,
                summary = filter.description
            )
        )
    return oc

@route('%s/BaseSpotnet/Display_Filter' % Settings.APP_PREFIX , page=int , filter=int)
def display_filter(filter , page=0):
    if int(filter) == 99999:                                # we are displaying an search query
        filter = Filter(Settings.QUEUE['filter'])
        del Settings.QUEUE['filter']
    else:
        filter = Settings.FILTER_DB.get_filter(int(filter))
    posts = Settings.POST_DB.get_posts_by_filter(filter , page * Settings.POST_PER_PAGE , Settings.POST_PER_PAGE)
    oc = ObjectContainer(no_cache=True)
    for post in posts:
        oc.add(
            DirectoryObject(
                key = Callback(display_post , messageid=post.messageid),
                title = post.title,
                tagline = "date %s" % post.posted,
                summary = post.description_markup,
                thumb = post.image
            )
        )
    oc.add(
        NextPageObject(
            key = Callback(display_filter , filter=filter.id , page=page+1),
            summary = 'Display the next %d posts' % Settings.POST_PER_PAGE
        )
    )
    return oc

@route('%s/BaseSpotnet/Display_Post' % Settings.APP_PREFIX , messageid=str)
def display_post(messageid):
    messageid = str(messageid)
    post = Settings.POST_DB.get_post_form_database(messageid)
    oc = ObjectContainer(
        art = post.image,
        objects = [
            DirectoryObject(
                key = Callback(dummy),
                title = "Description",
                thumb = post.image,
                summary = post.description_markup
            ),
            DirectoryObject(
                key = Callback(dummy),
                title = "Subcategories",
                thumb = post.image,
                summary = post.subcategories_markup
            ),
            DirectoryObject(
                key = Callback(dummy),
                title = "Date",
                thumb = post.image,
                summary = str(post.posted)
            ),
            DirectoryObject(
                key = Callback(post_openUrl , url = post.website),
                title = "Go to site",
                thumb = post.image,
                summary = post.description_markup
            ),
            PopupDirectoryObject(
                key = Callback(post_download , messageid = messageid),
                title = "Download spot",
                thumb = post.image,
                summary = post.description_markup
            )
        ]
    )
    return oc

@route('%s/BaseSpotnet/Open_Url' % Settings.APP_PREFIX)
def post_openUrl(url):
    webbrowser.open(url, new=1, autoraise=True)
    return ObjectContainer(header="Opening website", message="Opening website, %s" % url)

@route('%s/BaseSpotnet/Download_Post' % Settings.APP_PREFIX)
def post_download(messageid):
    post = Settings.POST_DB.get_post_form_database(messageid)
    con = Connection(True)
    post.get_nzb_content(con)
    con.disconnect()
    respons = SABnzbd.Helper.add_spotnet_post(post)
    if "Error" in respons:
        oc = ObjectContainer(
            DirectoryObject(
                key = Callback(dummy),
                title = "Error : %s" % respons['Error'],
            ),
        )
    else:
        oc = ObjectContainer(
            DirectoryObject(
                key = Callback(dummy),
                title = "Done",
            ),
        )
    return oc

@route('%s/BaseSpotnet/Search' % Settings.APP_PREFIX)
def search(**kwargs):
    return Search.search(**kwargs)

@route('%s/BaseSpotnet/Dummy' % Settings.APP_PREFIX)    
def dummy():
    pass    
