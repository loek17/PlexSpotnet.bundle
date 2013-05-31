import re


class Filter(object):

    def __init__(self , fdict = {}):
        self.id = fdict.get("__id__" , None)                                                                    #int        for finding our filter back in database
        self.name = unicode(fdict.get("name" , None)) if fdict.get("name" , None) is not None else None                            #unicode    name of filter
        self.description = unicode(fdict.get("description" , None)) if fdict.get("description" , None) is not None else None    #unicode    description of filter
        self.query = unicode(fdict.get("query" , None)) if fdict.get("query" , None) is not None else None                        #unicode    #regex 
        self.poster = unicode(fdict.get("poster" , None)) if fdict.get("poster" , None) is not None else None                    #unicode    #==
        self.tag = unicode(fdict.get("tag" , None)) if fdict.get("tag" , None) is not None else None                            #unicode    #==
        self.website = unicode(fdict.get("website" , None)) if fdict.get("website" , None) is not None else None                #unicode    #==
        self.max_age = int(fdict.get("max_age" , 0))                                                            #int        #is bigger
        self.category_code = int(fdict.get("category_code" , 0))                                                #int        #==
        self.subcategory_codes = fdict.get("subcategory_codes" , {})                                            #dict         #is in for 
        self.porn = fdict.get("porn" , False)                                                                    #bool        #==

    def get_request(self):
        req = "True"    #dummy to start te proces we don't now where the first "and" will be
        rdict = {}
        if self.query is not None:
            squery = re.compile(r'\b({0})\b'.format(self.query), flags=re.IGNORECASE)
            req = req + " and squery.match(title) and squery.match(description)"
            rdict["squery"] = squery
        if self.poster is not None:
            req = req + " and poster==sposter"
            rdict["sposter"] = self.poster
        if self.tag is not None:
            req = req + " and tag==stag"
            rdict["stag"] = self.tag
        if self.website is not None:
            req = req + " and website==swebsite"
            rdict["swebsite"] = self.website
        if self.category_code is not None:
            req = req + " and category==scategory"
            rdict["scategory"] = self.category_code
        if self.subcategory_codes is not None and isinstance(self.subcategory_codes , dict):
            i=0
            for format , list in self.subcategory_codes.iteritems():
                req = req + " and (False" #dummy to start te proces we don't now where the first "or" will be
                for cat in list:
                    sub = "sub%d" % i
                    req = req + " or %s[1:-1] in subcategory_codes"     % sub    #we need to add [1:-1] to prevent the "-" and "\n" being add by buzhug
                    rdict[sub] = "0%d%s%d" % (self.category_code, format, cat)
                    i = i+1
                req = req + ")"
        if self.max_age is not None and self.max_age > 0:
            date = Datetime.Now() - Datetime.Delta(days=self.max_age)
            req = req + " and posted > date"
            rdict["date"] = date
        if self.porn is False and self.category_code is not None and self.category_code==1:
            req = req + (" and not ( ptype[1:-1] in subcategory_codes" 
                        " or pgerne1[1:-1] in subcategory_codes" 
                        " or pgerne2[1:-1] in subcategory_codes" 
                        " or pgerne3[1:-1] in subcategory_codes" 
                        " or pgerne4[1:-1] in subcategory_codes"
                        " or pgerne11[1:-1] in subcategory_codes"
                        " or pgerne12[1:-1] in subcategory_codes"
                        " or pgerne13[1:-1] in subcategory_codes"
                        " or pgerne14[1:-1] in subcategory_codes"
                        " or pgerne15[1:-1] in subcategory_codes"
                        " or pgerne16[1:-1] in subcategory_codes"
                        " or pgerne17[1:-1] in subcategory_codes"
                        " or pgerne18[1:-1] in subcategory_codes"
                        " or pgerne19[1:-1] in subcategory_codes"
                        " or pgerne20[1:-1] in subcategory_codes"
                        " or pgerne21[1:-1] in subcategory_codes"
                        " or pgerne22[1:-1] in subcategory_codes"
                        " or pgerne23[1:-1] in subcategory_codes"
                        " or pgerne24[1:-1] in subcategory_codes"
                        " or pgerne25[1:-1] in subcategory_codes"
                        " or pgerne26[1:-1] in subcategory_codes"
                        " or pgerne27[1:-1] in subcategory_codes"
                        " or pgerne28[1:-1] in subcategory_codes )"
                        )#apporces type = d , codes = 23,24,25,26 and 72 tot 89 and type=z code = 03  (porn catorgries)
            rdict["ptype"] = "01z03" 
            rdict["pgerne1"] = "01d23"
            rdict["pgerne2"] = "01d24"
            rdict["pgerne3"] = "01d25"
            rdict["pgerne4"] = "01d26"
            rdict["pgerne11"] = "01d72"
            rdict["pgerne12"] = "01d73"
            rdict["pgerne13"] = "01d74"
            rdict["pgerne14"] = "01d75"
            rdict["pgerne15"] = "01d76"
            rdict["pgerne16"] = "01d77"
            rdict["pgerne17"] = "01d78"
            rdict["pgerne18"] = "01d79"
            rdict["pgerne19"] = "01d80"
            rdict["pgerne20"] = "01d81"
            rdict["pgerne21"] = "01d82"
            rdict["pgerne22"] = "01d83"
            rdict["pgerne23"] = "01d84"
            rdict["pgerne24"] = "01d85"
            rdict["pgerne25"] = "01d86"
            rdict["pgerne26"] = "01d87"
            rdict["pgerne27"] = "01d88"
            rdict["pgerne28"] = "01d89"
        return req , rdict

    def get_dict(self):
        return {"id" : self.id , "name" : self.name , "description" : self.description , "query" : self.query , "poster" : self.poster , "tag" : self.tag , "website" : self.website , "max_age" : self.max_age , "category_code" : self.category_code , "subcategory_codes" : self.subcategory_codes , "porn" : self.porn}
