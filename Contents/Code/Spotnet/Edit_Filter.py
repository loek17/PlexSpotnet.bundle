import Settings
Settings.load()

@route('%s/EditFilter/Display_Catorgies' % Settings.APP_PREFIX)
def display_categories():
    oc = ObjectContainer(
        objects = [
            DirectoryObject(
                key = Callback(edit_filter , cat=1),
                title = "Beeld"
            ),
            DirectoryObject(
                key = Callback(edit_filter , cat=2),
                title = "Music"
            ),
            DirectoryObject(
                key = Callback(edit_filter , cat=3),
                title = "Games"
            ),
            DirectoryObject(
                key = Callback(edit_filter , cat=4),
                title = "Applications"
            )
        ]
    )
    return oc

@route('%s/EditFilter/Edit_Filter' % Settings.APP_PREFIX  , cat=int)
def edit_filter(cat):
    filters = Settings.FILTER_DB.get_filters(cat)
    oc = ObjectContainer(
        no_cache = True,
        objects = [
            DirectoryObject(
                key = Callback(add_filter , cat = cat),
                title = "New filter",
                summary = "Create a new filter"
            )
        ]
    )
    for filter in filters:
        oc.add(
            PopupDirectoryObject(
                key = Callback(edit_filter_ask , filterid = filter.id , cat = cat),
                title = filter.name,
                summary = filter.description,
            )
        )
    return oc

@route('%s/EditFilter/Edit_Filter_Ask' % Settings.APP_PREFIX , cat=int)
def edit_filter_ask(filterid , cat):
    oc = ObjectContainer(
        objects = [
            DirectoryObject(
                key = Callback(add_filter , filter = filterid , cat = cat),
                title = "Edit filter",
            ),
            DirectoryObject(
                key = Callback(del_filter , filterid = filterid , cat = cat),
                title = "Delete filter",
            ),
            DirectoryObject(
                key = Callback(dummy),
                title = "Back",
            )
        ]
    )
    return oc

@route('%s/EditFilter/Del_Filter' % Settings.APP_PREFIX , cat=int)
def del_filter(filterid , cat):
    Settings.FILTER_DB.del_filter(filterid)

@route('%s/EditFilter/Add_Filter' % Settings.APP_PREFIX , cat=int)
def add_filter(filter = None , cat = 0):
    if "filter" not in Settings.QUEUE:
        if isinstance( filter, ( int, long ) ):
            Settings.QUEUE["filter"] = Spotnet.get_filter(filter).get_dict()
        else:
            Settings.QUEUE["filter"] = {"category_code" : cat}
    filter = Settings.QUEUE["filter"]
    oc = ObjectContainer(
        no_cache = True,
        objects = [
            InputDirectoryObject(
                key = Callback(set_new_filter , set="name"),
                title = "Name",
                summary = "The name of the filter \n Current : " + str(filter.get("name" , "Nothing set")),
                prompt = "The name of the filter"
            ),
            InputDirectoryObject(
                key = Callback(set_new_filter , set="description"),
                title = "Description",
                summary = "The description of the filter \n Current : " + str(filter.get("description" , "Nothing set")),
                prompt = "The description of the filter"
            ),
            DirectoryObject(#PopupDirectoryObject(            #only if plex devs can fix inputdirectory call from popup
                key = Callback(set_filter_ask , set="query", prompt = "Search query to search for"),
                title = "Search query to search for",
                summary = "Both title and description are searched \n Current Query : " + str(filter.get("query" , "Nothing set"))
            ),
            DirectoryObject(#PopupDirectoryObject(
                key = Callback(set_filter_ask , set="poster" , prompt = "Poster to match in the spot"),
                title = "Poster",
                summary = "Poster to match in the spot \n Current Poster : " + str(filter.get("poster" , "Nothing set"))
            ),
            DirectoryObject(#PopupDirectoryObject(
                key = Callback(set_filter_ask , set="tag" , prompt = "Tag to match in the spot"),
                title = "Tag",
                summary = "Tag to match in the spot \n Current Tag : " + str(filter.get("tag" , "Nothing set"))
            ),
            DirectoryObject(#PopupDirectoryObject(
                key = Callback(set_filter_ask , set="website" , prompt = "Website to match in the spot"),
                title = "Website",
                summary = "Website to match in the spot \n Current Website : " + str(filter.get("website", "Nothing set"))
            ),
            DirectoryObject(#PopupDirectoryObject(
                key = Callback(set_filter_ask , set="max_age" , prompt = "Max age , only insert numbers"),
                title = "Maximal Age",
                summary = "Max age the spot are \n 0=everthing \n Current age : " + str(filter.get("max_age" , "Nothing set"))
            ),
            PopupDirectoryObject(
                key = Callback(set_filter_type),
                title = "Subcategories",
                summary = "Select subcategories, only 1 of the subcategories for each type has to match"
            ),
            PopupDirectoryObject(
                key = Callback(set_filter_porn , set="porn"),
                title = "Porn",
                summary = "Display or Hide pornorafic material \n " + ("Visable" if filter.get("porn" , False) else "Hidden")
            ),
            PopupDirectoryObject(
                key = Callback(save_filter),
                title = "Save Filter",
                summary = "Save the filter"
            )
        ]
    )
    return oc

@route('%s/EditFilter/Set_Filter_Ask' % Settings.APP_PREFIX)
def set_filter_ask(prompt , **kwargs):
    oc = ObjectContainer(
        no_history = True ,
        no_cache = True,
        objects = [
            InputDirectoryObject(
                key = Callback(set_new_filter , **kwargs),
                title = "Update",
                summary = prompt,
                prompt = prompt
            ),
            DirectoryObject(
                key = Callback(del_new_filter , **kwargs),
                title = "Remove"
            )#,
            #DirectoryObject(        #only if plex devs can fix inputdirectory call from popup
            #    key = Callback(dummy),
            #    title = "Back"
            #)
        ]
    )
    return oc

@route('%s/EditFilter/Set_Filter_Porn' % Settings.APP_PREFIX)
def set_filter_porn(**kwargs):
    oc = ObjectContainer(
        objects = [
            DirectoryObject(
                key = Callback(set_new_filter , arg=False , **kwargs),
                title = "Hide Porn"
            ),
            DirectoryObject(
                key = Callback(set_new_filter , arg=True , **kwargs),
                title = "Display Porn"
            )
        ]
    )
    return oc

#popup
@route('%s/EditFilter/Set_Filter_Type' % Settings.APP_PREFIX)
def set_filter_type():
    oc = ObjectContainer()
    filter = Settings.QUEUE["filter"]
    for k,v in Settings.SUBCATEGORY_TYPE_MAPPING[filter["category_code"]].iteritems():
        oc.add(
            DirectoryObject(
                key = Callback(set_filter_subcategories , type = k),
                title = v
            )
        )
    return oc

@route('%s/EditFilter/Set_Filter_Subcategories' % Settings.APP_PREFIX , type=int)
def set_filter_subcategories(type):
    oc = ObjectContainer(no_cache = True )
    filter = Settings.QUEUE["filter"]
    for k,v in Settings.SUBCATEGORY_MAPPING[filter["category_code"]][type].iteritems():
        selected = False
        summary = "Not selected"
        if "subcategory_codes" in filter and type in filter["subcategory_codes"] and k in filter["subcategory_codes"][type]:
            selected = True
            summary = "Selected"
        oc.add(
            PopupDirectoryObject(
                key = Callback(set_filter_subcategory , type = type , subcat = k , selected = selected),
                title = v,
                summary = summary
            )
        )
    return oc

#popup
@route('%s/EditFilter/Set_Filter_Subcategory' % Settings.APP_PREFIX , selected = bool)
def set_filter_subcategory(type , subcat , selected):
    if selected:
        oc = ObjectContainer(
            objects = [
                DirectoryObject(
                    key = Callback(del_new_filter , set = "subcategory_codes"  , arg= {type : [subcat]}),
                    title = "Remove form filter"
                ),
                DirectoryObject(
                    key = Callback(dummy),
                    title = "Back"
                )
            ]
        )
    else:
        oc = ObjectContainer(
            objects = [
                DirectoryObject(
                    key = Callback(set_new_filter , set = "subcategory_codes" , arg= {type : [subcat]}),
                    title = "Add to filter"
                ),
                DirectoryObject(
                    key = Callback(dummy),
                    title = "Back"
                )
            ]
        )
    return oc

@route('%s/EditFilter/Set_New_Filter' % Settings.APP_PREFIX)
def set_new_filter(set , arg=None , **kwargs):
    filter = Settings.QUEUE["filter"]
    if arg is None:
        arg = kwargs.get("query" , None)
        del kwargs["query"]
    if arg is not None:
        if isinstance(arg , dict):
            filter[set] = {} if set not in filter else filter[set]
            for k , v in arg.iteritems():
                if isinstance(v , list):
                    if k in filter[set]:
                        filter[set][k] = filter[set][k] + v
                    else:
                        filter[set][k] = v
                else:
                    if k in filter[set]:
                        filter[set][k].append(v)
                    else:
                        filter[set][k] = [v]
        else:
            filter[set] = arg
    Settings.QUEUE["filter"] = filter

@route('%s/EditFilter/Del_New_Filter' % Settings.APP_PREFIX)
def del_new_filter(set ,arg = None):
    filter = Settings.QUEUE["filter"]
    if set in filter:
        if isinstance(arg , dict):
            filter[set] = {} if set not in filter else filter[set]
            for k , v in arg.iteritems():
                if k in filter[set]:
                    if isinstance(v , list):    #allows us to delete list op subs, do we need this
                        for x in v:
                            filter[set][k].remove(x)
                    else:
                        filter[set][k].remove(v)
        else:
            del filter[set]
    Settings.QUEUE["filter"] = filter     

@route('%s/EditFilter/Save_Filter' % Settings.APP_PREFIX)
def save_filter():
    filter = Settings.QUEUE["filter"]
    Log.Info(filter)
    if filter.get("name" , False):
        Settings.FILTER_DB.add_filter_to_database(Filter(filter))
        del Settings.QUEUE["filter"]
        oc = ObjectContainer(
            replace_parent = True,
            objects = [
                DirectoryObject(
                    key = Callback(dummy),#MainMenu),
                    title = "Done"
                )
            ]
        )
    else:
        oc = ObjectContainer(
            objects = [
                DirectoryObject(
                    key = Callback(dummy),
                    title = "Please, choose a filter name"
                )
            ]
        )
    return oc

@route('%s/EditFilter/Dummy' % Settings.APP_PREFIX)
def dummy():
    pass
