import Settings

UNKNOWN_TEXT = 'unknown'

def _(s):
    return s

def split_code(code):
    i = 0
    while code[i].isdigit():
        i += 1
    j = i
    while code[j].isalpha():
        j += 1
    return int(code[:i]), code[i:j], int(code[j:])

class Category:

    def __init__(self , code):
        Settings.load()
        self.code = int(code)
        try:
            self.category = Settings.CATEGORY_MAPPING[code]
        except:
            self.category = UNKNOWN_TEXT

    def is_valid(self):
        return self.code in Settings.CATEGORY_MAPPING

    @property
    def name(self):
        return self.category


class Subcategory:
    def __init__(self, code):
        Settings.load()
        self.code = code
        try:
            self.main_, self.type_, self.sub_ = split_code(code)
        except:
            raise ValueError("Got an invalid subcategory code %r" % self.code)

    def is_valid(self):
        return self.main_  in Settings.CATEGORY_MAPPING \
            and self.type_ in Settings.SUBCATEGORY_TYPE_MAPPING[self.main_] \
            and self.sub_  in Settings.SUBCATEGORY_MAPPING[self.main_][self.type_]

    @property
    def main(self):
        return _(Settings.CATEGORY_MAPPING.get(self.main_, UNKNOWN_TEXT))

    @property
    def type_base(self):
        cmap = Settings.SUBCATEGORY_TYPE_MAPPING.get(self.main_, {})
        return cmap.get(self.type_, UNKNOWN_TEXT)

    @property
    def type(self):
        return _(self.type_base)

    @property
    def sub(self):
        cmap = Settings.SUBCATEGORY_MAPPING.get(self.main_, {})
        ccmap = cmap.get(self.type_, {})
        return _(ccmap.get(self.sub_, UNKNOWN_TEXT))

    @property
    def name(self):
        return self.sub
"""
    def __init__(self, dict):
        self.main = dict['main']
        del dict['main']
        self.dict = dict

    def get_valid(self):
        dict = self.dict
        if self.main in Settings.CATEGORY_MAPPING:
            for type ,list in dict.iteritems():
                if type in Settings.SUBCATEGORY_TYPE_MAPPING[self.main]:
                    for num , cat in enumerate(list):
                        if cat not in Settings.SUBCATEGORY_MAPPING[self.main][type]:
                            del dict[type][num]
                else:
                    del dict[type]
        else:
            return {}
        return dict

    @property
    def formated(self):
        codes = self.get_valid()
        subs = {}
        for type ,list in dict.iteritems():
            for num , cat in enumerate(list):
                if subs.get(Settings.SUBCATEGORY_TYPE_MAPPING[self.main][type] , None):
                    subs[Settings.SUBCATEGORY_TYPE_MAPPING[self.main][type]].append(Settings.SUBCATEGORY_MAPPING[self.main][type][list[num]])
                else:
                    subs[Settings.SUBCATEGORY_TYPE_MAPPING[self.main][type]] = [Settings.SUBCATEGORY_MAPPING[self.main][type][list[num]]]
        return subs
"""




