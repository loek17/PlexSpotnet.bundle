import SabSettingsimport stringfrom base64 import b64encodeclass AuthError:    passdef get_auth():    if "auth" in SabSettings.QUEUE:        return SabSettings.QUEUE['auth']    base_url = "http://%s:%s/api" % (SabSettings.SABNZBD_IP , SabSettings.SABNZBD_POORT) if not SabSettings.SABNZBD_HTTPS else "https://%s:%s/api" % (SabSettings.SABNZBD_IP , SabSettings.SABNZBD_POORT)    url = base_url + "?mode=auth"    Log.Info(url)    auth = HTTP.Request(url , immediate=True).content    Log.Info(auth)    if auth == "None":        SabSettings.QUEUE['auth'] = "dummy=dummy"    elif "apikey" in auth:        # https://github.com/mikedm139/SABnzbd.bundle/blob/master/Contents/Code/__init__.py        url = base_url[:-4] + "/sabnzbd/config/general"        headers = {'Authorization': 'Basic ' + b64encode(SabSettings.SABUSER + ':' + SabSettings.SABPASS)} if SabSettings.SABUSER else {}        configPage = HTML.ElementFromURL(url, headers=headers)        api_key = configPage.xpath('//input[@id="apikey"]')[0].get('value')        SabSettings.QUEUE['auth'] = "apikey=%s" % api_key    elif auth == "login":        SabSettings.QUEUE['auth'] = "ma_username=%s&ma_password=%s" % (SabSettings.SABUSER , SabSettings.SABPASS)    else:        raise AuthError    return SabSettings.QUEUE['auth']def base_action(**kwargs):    base_url = "http://%s:%s/api" % (SabSettings.SABNZBD_IP , SabSettings.SABNZBD_POORT) if not SabSettings.SABNZBD_HTTPS else "https://%s:%s/api" % (SabSettings.SABNZBD_IP , SabSettings.SABNZBD_POORT)    auth = get_auth()    url = base_url + ("?%s" % auth) + ("&output=%s" % SabSettings.SABNZBD_MODE)    if 'header' in kwargs:        header = kwargs['header']        del kwargs['header']    if 'body' in kwargs:        body = kwargs['body']        del kwargs['body']    for key , arg in kwargs.iteritems():        if arg is not False:            url = url + ("&%s=%s" % (str(key) , str(arg)))    content = HTTP.Request(url , header=header , data=body , immediate=True).content    if content.startswith('error: '):        return {'Error' : content[len('error: '):]}    return JSON.ObjectFromString(content)def advanced_queue(start=None , limit=None):    return base_action(mode="queue" , start=start , limit=limit)def histroy(start=None , limit=None):    return base_action(mode="history" , start=start , limit=limit)def version():    return base_action(mode="version")def warnings():    return base_action(mode="warnings")def categories():    return base_action(mode="get_cats")    def scripts():    return base_action(mode="get_scripts")def restart():    return base_action(mode="restart")def queue_delete(ids="all"):    ids = list(ids)    str = False    for id in ids:        if str:            str = str + ",%s" % id        else:            str = id    return base_action(mode="queue" , name="delete" , value=str)def queue_swap(id1 , id2):    return base_action(mode="switch" , value=id1 , value2=id2)    def queue_move(id , place):    return base_action(mode="switch" , value=id , value2=place)def queue_pause(pause_time=False):    if pause_time:        return base_action(mode="config" , name="set_pause" , value=pause_time)    else:        return base_action(mode="pause")def queue_resume():    return base_action(mode="resume")def shutdown():    return base_action(mode="shutdown")    def add_url(url , name , **kwargs):    # kwargs accepts pp, script, cat, priority    return base_action(mode="addurl" , name=url , nzbname=name , **kwargs)def add_file(content , name , **kwargs):    # kwargs accepts pp, script, cat, priority        content_type , body = encode_multipart_formdata([("agent" , "Plex_spotnet")] , [("nzbfile" , "%s.nzb" % name , content)])    headers = {'content-type': content_type , 'content-length': str(len(body))}        return base_action(mode='addfile' , nzbname=name , header=headers , body=body , **kwargs)def encode_multipart_formdata(fields, files):    """    fields is a sequence of (name, value) elements for regular form fields.    files is a sequence of (name, filename, value) elements for data to be uploaded as files    Return (content_type, body) ready for httplib.HTTP instance    """    BOUNDARY = '----------%s' % ''.join (Util.RandomItemFromList(string.ascii_letters) for ii in range (30 + 1))    CRLF = '\r\n'    L = []    for (key, value) in fields:        L.append('--' + BOUNDARY)        L.append('Content-Disposition: form-data; name="%s"' % key)        L.append('')        L.append(value)    for (key, filename, value) in files:        L.append('--' + BOUNDARY)        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))        L.append('Content-Type: %s' % get_content_type(filename))        L.append('')        L.append(value)    L.append('--' + BOUNDARY + '--')    L.append('')    body = CRLF.join(L)    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY    return content_type, bodydef get_content_type(filename):    return 'application/octet-stream'#Resource.GuessMimeType(filename)[0] or 'application/octet-stream'def add_path(path , name , **kwargs):    # kwargs accepts pp, script, cat, priority    return base_action(mode="addlocalfile" , name=path , nzbname=name , **kwargs)def change_script(id , script):    return base_action(mode="change_script" , value=id , value2=script)def change_category(id , cat):    return base_action(mode="change_cat" , value=id , value2=cat)def action_on_compleet(action , script):    r_action = "script_%s" % action if script else action    return base_action(mode="queue" , name="change_compleet_action" , value=r_action)def change_post_proces(id , proces):    """    Description: Change value2 to control what post-processing option to use    Skip: 0    +Repair: 1    +Repair/Unpack: 2    +Repair/Unpack/Delete: 3    """    return base_action(mode="change_opts" , value=id , value2=proces)def change_post_priority(id , priority):    """    Description:    Default Priority: -100    Paused: -2    Low Priority: -1    Normal Priority: 0    High Priority: 1    """    return base_action(mode="queue" , name="priority" , value=id , value2=priority)def pause_individual(id):    return base_action(mode="queue" , name="pause" , value=id)def resume_individual(id):    return base_action(mode="queue" , name="resume" , value=id)def retrieve_individual_content(id):    return base_action(mode="get_files" , value=id)def change_name(id , name):    return base_action(mode="queue" , name="rename" , value=id , value2=name)def history_delete(ids , **kwargs):    """    all = delete all    failed = delete all failed    Extra parameters:    failed_only, when 1, delete only failed jobs    del_files when 1, all files will be deleted too (only for failed jobs)    """    ids = list(ids)    str = False    for id in ids:        if str:            str = str + ",%s" % id        else:            str = id    return base_action(mode="histroy" , name="delete" , value=str , **kwargs)def history_retry(id):    return base_action(mode="retry" , value=id)def set_speed_limit(limit):    return base_action(mode="config" , name="speedlimit" , value=limit)def set_config(section , keyword , value=False , **kwargs):    """    kwargs is for Setting a number of values in an RSS feed.    http://localhost:8080/sabnzbd/api?mode=set_config&section=rss&keyword=MyFeed&enable=1&pp=3    SABnzbd will return all the new settings for that feed as a result.    """    return base_action(mode="set_config" , section=section , keyword=keyword , value=value , **kwargs)def get_config(section=False , keyword=False):    """    You can read any subsection of the configuration.    Note that you will never receive passwords, each character will be replaced by a * character.    You can set new passwords through the set_config call.    """    return base_action(mode="get_config" , section=section , keyword=keyword)