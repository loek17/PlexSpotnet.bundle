from buzhug import TS_Base as Base
from Post import Post
from Filter import Filter
from SpotnetSettings import SpotSettings as Settings
import os

class PostDatabase:
    
    def __init__(self):
        Settings.load()
        self.sync_database()
        self.open = False
        self.db = Base(os.path.join(Settings.DB_DIR , 'Posts'))
        
    def sync_database(self):
        if not os.path.isdir(Settings.DB_DIR):
            os.mkdir(Settings.DB_DIR)
        if not os.path.isdir(os.path.join(Settings.DB_DIR , 'Posts')):
            from datetime import datetime
            try:
                self.db = Base(os.path.join(Settings.DB_DIR , 'Posts')).create(("messageid" , str) , ("postnumber" , float), ("poster" , unicode), ("title" , unicode), ("description" , unicode), ("tag" , unicode), ("posted" , datetime), ("category" , int), ("subcategory_codes" , list), ("image" , dict), ("website" , unicode), ("size" , float), ("nzb" , list))
            except:
                pass
    
    def add_post_to_database(self , post):
        # no need to open database because is opened by update_database
        if len(self.db(messageid = post.messageid)) == 0:
            self.db.insert(post.messageid , post.postnumber , post.poster , post.title , post.description , post.tag , post.posted , post.category_code , post.subcategory_codes , post.image_segs , post.website , post.size , post.nzb)
    
    def del_post_form_database(self , messageid):
        # no need to open database because is opened by update_database of cleanup
        # used for deleting desposed posts and cleanup
        oldSpot = self.db(messageid = messageid)
        try:
            os.unlink(Settings.IMAGE_DIR % oldSpot.image_segs['segment'][0].split("@")[0])
        except:
            pass
        self.db.delete(self.db(messageid = messageid))
        
    
    def get_post_form_database(self , messageid):
        if self.open:
            close = False
        else:
            self.db.open()
            close = True
        data = self.db(messageid = messageid)
        if close:
            self.db.close()
        return Post().from_database(data[0])
    
    def get_posts_by_filter(self , filter , start=0 , count = None):
        data = []
        i=0
        request , rdict = filter.get_request()
        if self.open:
            close = False
        else:
            self.db.open()
            close = True
        posts = self.db.select(None , request , **rdict).sort_by("-posted")[start:]
        if close:
            self.db.close()
        for post in posts:
            data.append(Post().from_database(post))
            i += 1
            if i == count: 
                return data
        return data
    
    def cleanup():
        date = Datetime.Now() - Datetime.Delta(days=Settings.MAX_AGE)
        old = self.db.select(None , "posted < min_date" , date=date)
        for oldSpot in old:
            try:
                os.unlink(Settings.IMAGE_DIR % oldSpot.image_segs['segment'][0].split("@")[0])
            except:
                pass
        self.db.delete(old)
        self.db.cleanup()

class FilterDatabase:
    
    def __init__(self):
        Settings.load()
        self.sync_database()
        self.db = Base(os.path.join(Settings.DB_DIR , 'Filters'))
        
    def sync_database(self):
        if not os.path.isdir(Settings.DB_DIR):
            os.mkdir(Settings.DB_DIR)
        if not os.path.isdir(os.path.join(Settings.DB_DIR , 'Filters')):
            try:
                self.db = Base(os.path.join(Settings.DB_DIR , 'Filters')).create(("name" , unicode),("description" , unicode),("query" , unicode),("poster" , unicode),   ("tag" , unicode), ("category_code" , int), ("subcategory_codes" , dict), ("max_age" , int) , ("porn" , bool))
            except:
                pass
            else:
                try:
                    for filter in Settings.DEFAULT_FILTERS:
                        self.add_filter_to_database(Filter(filter))
                except:
                    pass
    
    def get_filters(self , cat):
        data = []
        self.db.open()
        filters = self.db.select(None , category_code = cat)
        self.db.close()
        for filter in filters:
            data.append(Filter(filter))
        return data
    
    def get_filter(self , id):
        self.db.open()
        filter = self.db[id]
        self.db.close()
        return Filter(filter)
    
    def del_filter(self , id):
        self.db.open()
        del self.db[id]
        self.db.close()

