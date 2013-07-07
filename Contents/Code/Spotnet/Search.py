from SpotnetSettings import SpotSettings as Settings
import Edit_Filter

@route('%s/Search/Display_Categories' % Settings.APP_PREFIX)
def display_categories():
    oc = ObjectContainer(
        objects = [
            DirectoryObject(
                key = Callback(search , cat=1 , advanced = True),
                title = "Beeld"
            ),
            DirectoryObject(
                key = Callback(search , cat=2 , advanced = True),
                title = "Music"
            ),
            DirectoryObject(
                key = Callback(search , cat=3 , advanced = True),
                title = "Games"
            ),
            DirectoryObject(
                key = Callback(search , cat=4 , advanced = True),
                title = "Applications"
            )
        ]
    )
    return oc

@route('%s/Search/Search' % Settings.APP_PREFIX , cat=int)
def search(cat , advanced = False , query = None):
    if advanced:
        Settings.QUEUE['filter'] = {"category_code" : cat} if not Settings.QUEUE.get('filter' , False) else Settings.QUEUE['filter']
        oc = ObjectContainer(
            no_cache = True,
            objects = [
                DirectoryObject(#PopupDirectoryObject(
                    key = Callback(set_filter_ask , set="query" , prompt = "Search query to search for"),
                    title = "Search query to search for",
                    summary = "Both title and description are searched \n Current Query : " + str(Settings.QUEUE['filter'].get("query" , "Nothing set"))
                ),
                DirectoryObject(#PopupDirectoryObject(
                    key = Callback(set_filter_ask , set="poster" , prompt = "Poster to match in the spot"),
                    title = "Poster",
                    summary = "Poster to match in the spot \n Current Poster : " + str(Settings.QUEUE['filter'].get("poster" , "Nothing set"))
                ),
                DirectoryObject(#PopupDirectoryObject(
                    key = Callback(set_filter_ask , set="tag" , prompt = "Tag to match in the spot"),
                    title = "Tag",
                    summary = "Tag to match in the spot \n Current Tag : " + str(Settings.QUEUE['filter'].get("tag" , "Nothing set"))
                ),
                DirectoryObject(#PopupDirectoryObject(
                    key = Callback(set_filter_ask , set="website" , prompt = "Website to match in the spot"),
                    title = "Website",
                    summary = "Website to match in the spot \n Current Website : " + str(Settings.QUEUE['filter'].get("website", "Nothing set"))
                ),
                DirectoryObject(#PopupDirectoryObject(
                    key = Callback(set_filter_ask , set="max_age" , prompt = "Max age , only insert numbers"),
                    title = "Maximal Age",
                    summary = "Max age the spot are \n 0=everthing \n Current max age : " + str(Settings.QUEUE['filter'].get("max_age" , "Nothing set"))
                ),
                PopupDirectoryObject(
                    key = Callback(set_filter_type),
                    title = "Subcategories",
                    summary = "Select subcategories, only 1 of the subcategories for each type has to match"
                ),
                PopupDirectoryObject(
                    key = Callback(set_filter_porn , set="porn"),
                    title = "Porn",
                    summary = "Display or Hide pornorafic material \n " + ("Visable" if Settings.QUEUE['filter'].get("porn" , False) else "Hidden")
                ),
                DirectoryObject(
                    key = Callback(display_filter),
                    title = "Search Now",
                    summary = "Search with the selected settings"
                )
            ]
        )
        return oc
    else:
        Settings.QUEUE['filter'] = {"category_code" : cat , "query" : query}
        return display_filter(filter = 99999)
    
@route('%s/Search/Set_Filter_Ask' % Settings.APP_PREFIX)
def set_filter_ask(**kwargs):
    return Edit_Filter.set_filter_ask(**kwargs)

@route('%s/Search/Set_Filter_Type' % Settings.APP_PREFIX)
def set_filter_type(**kwargs):
    return Edit_Filter.set_filter_type(**kwargs)

@route('%s/Search/Set_Filter_Porn' % Settings.APP_PREFIX)
def set_filter_porn(**kwargs):
    return Edit_Filter.set_filter_porn(**kwargs)

@route('%s/Search/Display_Filter' % Settings.APP_PREFIX)
def display_filter():
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

@route('%s/Search/Dummy' % Settings.APP_PREFIX)
def dummy():
    pass
