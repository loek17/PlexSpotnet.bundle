
#from dateutil.parser import parse as parse_datetime
#from xml.dom.minidom import parseString
#from datetime import datetime, timedelta
from Decode import decode_nzb, DecodeNzbError
from Subcategories import Subcategory , Category
import Settings
#import cPickle as pickle
#from datetime import datetime
import re 

class InvalidPost(Exception):
    pass


class RawPost:

    # PUBLIC ATTRIBUTES:
    # messageid     : string, like <xxx@spot.net>
    # postnumber    : integer (server dependent!)
    # poster        : string, name of the poster
    # title         : string, post title
    # description   : string, post description
    # tag           : string or None, post tag
    # posted        : datetime.datetime, post creation moment
    # category      : int, indication of category
    # subcategory   : (possibly empty) list of strings, indication of subcategories
    # image         : string or None, http adress of post image or list of messageids that make the image
    # website       : sting or None, http adress of additional post info
    # size          : int or None, byte size of files in post
    # nzb           : list of strings, messageids of posts that, together, contain the nzb file
    #                  use a RawNzbPost object to get the actual nzb file from these messageids
    #
    # PUBLIC METHODS:
    # verify_post()     : bool,
    # verify_poster()   : bool,
    #

    # RAW POST DESCRIPTION:
    # [0] : '220 0 <0d7IZVT9wjIJqcSTgAYLN@spot.net> article' : status ? messageid type
    # [1] : '0' : ?
    # [2] : '<0d7IZVT9wjIJqcSTgAYLN@spot.net>' : messageid
    # [3] : '...' : body
    # body:
    # NOTE THAT SOME HEADERS ARE SPREAD OVER SEVERAL LINES!
    # - Path                        : 'news.hitnews.eu!not-for-mail'
    # - From                        : 'kww <132200@13a05b03.42638314.132200.1309845303.JnY.so8.EuS-sqx-s>'
    # - Subject
    # - Newsgroups
    # - Message-ID
    # - X-XML
    # - X-XML
    # - X-XML-Signature             : 'cUWupZtWsQAhp4WLYg-pwT00ab-sJvdMQnKWu1kDETInZowAc06x-pBW3-sIWT0D7VuQ' : signature of xml
    # - X-User-Key                  : '<RSAKeyValue><Modulus>szsAIT5W5</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>'
    # - X-User-Signature            : 'Mh-sbcEHnIR-pNRVHFtPP-sxHTTTFu7S1vkmOterGBKGNCIcwyN5Xo7BQxaFtq0FgRd'
    # - Content-Type                : 'text/plain; charset=ISO-8859-1' : mime-type; encoding
    # - Content-Transfer-Encoding   : '8bit' : ?
    # - Date
    # - Lines                       : Number of lines following headers that make up the body
    # - Organization                : Organization that originally posted this post
    # - NNTP-Posting-Host           : == Organization(?)
    # - X-Complaints-To             : Email adress to notify in case of abuse
    # [empty line]
    # Remaining lines (>1!) make up the body
    #    the amount of lines here is passed as header 'Lines'

    def __init__(self, postnumber, rawpost):
        #Log.Info('raw post created in init function')
        Settings.load()
        self.postnumber_dump = int(postnumber) if postnumber is not None else None
        self.messageid = rawpost[2]
        self.rawpost = rawpost
        self.content_is_nzb = None
        try:
            self.content = self.parse_rawpost_content(self.rawpost[3])
        except InvalidPost:
            raise
        except Exception as e:
            raise InvalidPost(
                "Error in parsing raw post content, exception was '%s'" % e
            )
        try:
            self.extra = self.parse_xml_content(self.content['X-XML'])
        except (KeyError, InvalidPost):
            self.extra = {}
        except:
            raise InvalidPost('Error in parsing raw post content')

    def parse_rawpost_content(self, content):
        #Log.Info('in parse raw content function')
        d = {}
        content_length = len(content)
        l = -1
        # find Lines header
        for num, line in enumerate(content):
            if line.startswith('Lines: '):
                l = num
                break
        if l == 0:
            raise InvalidPost("Post does not have a Lines header.")
        body_lines = int(content[l][len('Lines: '):])
        last_header = None
        for l in xrange(len(content) - body_lines - 1):
            if ':' in content[l]:
                k, v = content[l].split(': ', 1)
                if k in d:
                    d[k] = d[k] + str(v)
                else:
                    d[k] = v
                last_header = k
            else:
                # we only allow an empty line, or a continuation here!
                if content[l] != '':
                    if content[l][0] == ' ':
                        if last_header:
                            d[k] = d[k] + v
                        else:
                            raise InvalidPost(
                                "Post has invalid header first line '%s'" % content[l]
                            )
                    else:
                        raise InvalidPost(
                            "Post has invalid header line '%s'" % content[l]
                        )
            l += 1
        if not content[l] == '':
            raise InvalidPost("First line after headers is not empty!")
        if not len(content) == int(d['Lines']) + l + 1:
            raise InvalidPost(
                "Header value for Lines differs from "
                "actual number of lines!"
            )
        return d

    def parse_xml_content(self, xml_string):
        #Log.Info('in parse xml content function')
        #try:
        #    xml = parseString(xml_string)
        #except:
        #    raise InvalidPost("Post has invalid XML data for header X-XML")
        #doc = xml.documentElement
        doc = XML.ElementFromString(xml_string)
        if not doc.tag == 'Spotnet':
            raise InvalidPost(
                "XML for spotnet post does not have a main "
                "node called 'Spotnet'"
            )
        if not len(doc.getchildren()) == 1:
            raise InvalidPost(
                "XML for spotnet post does not have 1 child "
                "for main node 'Spotnet'"
            )
        main = doc.getchildren()[0]
        if not main.tag == 'Posting':
            raise InvalidPost(
                "XML for spotnet post does not have a main "
                "child node called 'Posting' for 'Spotnet'"
            )
        # assemble dict of content
        d = {}
        for e in main:
            if len(e.getchildren()) == 0 and e.text != '':
                # if it has one child that is a textnode or cdata node, add it to the dict
                d[e.tag] = e.text
            elif e.tag == 'Category':                        # TODO
                d['Category'] = e.xpath("text()")
                d['Subcategories'] = []
                for cat_node in e:
                    # a sub category
                    d['Subcategories'].append(cat_node.text)
            elif e.tag == 'NZB':
                # we give this nzb dict the same name as the tag
                # so that _if_ an nzb only contains one textnode with
                # the location, the result is similar (a string instead of a string list)
                d['NZB'] = []
                for nzb_node in e:
                    if not nzb_node.tag == 'Segment':
                        raise InvalidPost(
                            "XML for spotnet post, in NZB node "
                            "there are child nodes that are not named 'Segment'"
                        )
                    d['NZB'].append(nzb_node.text)
            elif e.tag == 'Image':
                d['Image'] = {}
                for name, value in sorted(e.items()):
                    d['Image'][name] = value
                if len(e.getchildren()) > 0:
                    d['Image']['segment'] = []
                    for seg in e:
                        d['Image']['segment'].append(seg.text)
        if isinstance(d.get('Category', None), list):
            if len(d['Category']) == 0:
                d['Category'] = 0
            else:
                d['Category'] = d['Category'][0]
        if isinstance(d.get('NZB', None), basestring):
            d['NZB'] = [d['NZB']]
        return d

    def decode_string(self, string):
        #Log.Info('in decode string function')
        if string is None or isinstance(string, unicode):
            return string
        elif isinstance(string, str):
            return string.decode('utf8', 'replace')
        else:
            raise TypeError(string)

    def get_content(self):
        #Log.Info('in get content function')
        return ''.join(self.rawpost[3][-int(self.content['Lines']):])

    def check_content_is_nzb(self):
        #Log.Info('in check content is nzb function')
        if self.content_is_nzb is None:
            content = self.get_content()
            if content.startswith('=ybegin'):
                try:
                    # TODO: yenc decoding and possibly some more
                    # because this alone never seems to work
                    ydecoded = content  # TODO
                    decode_nzb(ydecoded)
                except DecodeNzbError:
                    self.content_is_nzb = False
                else:
                    self.content_is_nzb = True
                self.content_is_nzb = True  # TODO
            else:
                self.content_is_nzb = False
        return self.content_is_nzb

    # public properties
    @property
    def postnumber(self):
        try:
            return float(self.postnumber_dump) if self.postnumber_dump is not None else None
        except:
            return None

    @property
    def poster(self):
        p = self.content['From'].split('<', 1)[0].strip()
        return self.decode_string(p)

    @property
    def subject(self):
        if 'Title' in self.extra:
            return self.decode_string(self.extra['Title'])
        else:
            subj = self.content['Subject']
            if ' | ' in subj:
                subj, poster = subj.split(' | ', 1)
            return self.decode_string(subj)

    @property
    def description(self):
        if 'Description' in self.extra:
            return self.decode_string(self.extra['Description'])
        if self.check_content_is_nzb():
            return u''
        else:
            return self.decode_string(self.get_content())

    @property
    def tag(self):
        return self.decode_string(self.extra.get('Tag', None))

    @property
    def posted(self):
        # TODO:
        # This has to be rewritten to use django's new timezone support.
        # The NNTP-Posting-Date header is not mandatory, but does contain
        # timezonde data (always?) and can thus be used to get the tz.
        # If that's not available, another fallback is the Created
        # header can supply the creation datetime, but it does not contain
        # timezone info, so we must make assumptions.
        # Note that the 'Date' header is the only one usefull here
        # that is required, but does not supply time info.

        dt_str = self.content['Date']
        try:
            return Datetime.ParseDate(dt_str)    #datetime.strptime(str(Datetime.ParseDate(dt_str)) , "YYYY-MM-DD HH:MM:SS")    #not nice but works well
        except ValueError:
            raise InvalidPost('Invalid header value for Date: %r' % dt_str)

    @property
    def category(self):
        return int(self.extra.get('Category', 0))

    @property
    def subcategories(self):
        """retr = {}
        retr['main'] = self.category
        for sub in [self.decode_string(x) for x in self.extra.get('Subcategories', []) if x]:
            sub = self.split_code(sub)
            if sub[0] == '0'+str(retr['main']):
                sub[1] = sub[1][-1] if len(sub[1]) > 1 else sub[1]
                if retr.get(sub[1] , None):
                    retr[sub[1]].append(sub[2]) 
                else:
                    retr[sub[1]] = [sub[2]]
        return retr
        """
        return [self.decode_string(x) for x in self.extra.get('Subcategories', []) if x]

    @property
    def image(self):
        return self.extra.get('Image', None)

    @property
    def website(self):
        return self.decode_string(self.extra.get('Website', None))

    @property
    def size(self):
        try:
            x = self.extra.get('Size', None)
            return float(x) if x is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def nzb(self):
        if 'NZB' in self.extra:
            nzb_raw = self.extra['NZB']
            return [self.decode_string(x) for x in nzb_raw]
        if self.check_content_is_nzb():
            return [self.decode_string(self.messageid)]
        else:
            return []

class PostMarker:

    def __init__(self , messageid , person_id , is_good):
        pass

class Post:

    def __init__(self):
        Settings.load()
        self.nzb_website = False
        self.nzb_content = None
        
    def form_rawpost(self , rawpost):
        self.messageid = rawpost.messageid            #str
        self.postnumber = rawpost.postnumber        #float
        self.poster = rawpost.poster                #unicode
        self.title = rawpost.subject                #unicode
        self.description = rawpost.description        #unicode
        self.tag = rawpost.tag                        #unicode
        self.posted = rawpost.posted                #datetime
        self.category_code = rawpost.category        #int
        self.subcategory_codes = rawpost.subcategories     #list
        self.image_segs = rawpost.image                    #dict
        self.website = rawpost.website                #unicode
        self.size = rawpost.size                    #float
        self.nzb = rawpost.nzb                        #list
        return self
    
    def from_database(self , data):
        self.messageid = data.messageid
        self.postnumber = data.postnumber
        self.poster = data.poster
        self.title = data.title
        self.description = data.description
        self.tag = data.tag
        self.posted = data.posted
        self.category_code = data.category
        self.subcategory_codes = data.subcategory_codes
        self.image_segs = data.image
        self.website = data.website
        self.size = data.size
        self.nzb = data.nzb
        return self
    
    def has_nzb(self):
        return len(self.nzb) > 0
    
    def has_image(self):
        if self.image_segs and len(self.image_segs['segment'])>0:
            return True
        return False

    def is_porn(self):
        return "01z03" in self.subcategory_codes \
                or "01d23" in self.subcategory_codes \
                or "01d24" in self.subcategory_codes \
                or "01d25" in self.subcategory_codes \
                or "01d26" in self.subcategory_codes \
                or "01d72" in self.subcategory_codes \
                or "01d73" in self.subcategory_codes \
                or "01d74" in self.subcategory_codes \
                or "01d75" in self.subcategory_codes \
                or "01d76" in self.subcategory_codes \
                or "01d77" in self.subcategory_codes \
                or "01d78" in self.subcategory_codes \
                or "01d79" in self.subcategory_codes \
                or "01d80" in self.subcategory_codes \
                or "01d81" in self.subcategory_codes \
                or "01d82" in self.subcategory_codes \
                or "01d83" in self.subcategory_codes \
                or "01d84" in self.subcategory_codes \
                or "01d85" in self.subcategory_codes \
                or "01d86" in self.subcategory_codes \
                or "01d87" in self.subcategory_codes \
                or "01d88" in self.subcategory_codes \
                or "01d89" in self.subcategory_codes

    @property
    def description_markup(self):
        retr = u"%s \n\n%s" % (re.sub('\[[^>]\]' , '' , unicode(self.description).replace('[br]', '\n')) , self.subcategories_markup)
        return retr

    @property
    def category(self):
        return Category(self.category_code)

    @property
    def subcategories(self):
        s = self.subcategory_codes
        return (Subcategory(code) for code in self.subcategory_codes)
        
    @property
    def subcategories_markup(self):
        retr = ""
        idict = {"Website" : [self.website] , "Poster" : [self.poster] , "Tag" : [self.tag] , "Category" : [Settings.CATEGORY_MAPPING[self.category_code]]}
        for sub in self.subcategories:
            if sub.is_valid():
                if sub.type_base in idict:
                    idict[sub.type_base].append(sub.name)
                else:
                    idict[sub.type_base] = [sub.name]
        #add subcategories to summary
        for type in sorted(idict):
            retr = retr + type + " : "
            for sub in idict[type]:
                retr = unicode(retr) + unicode(sub) + ", "
            retr = unicode(retr) + "\n"
        return retr
    
    @property
    def date(self):
        return self.posted.strftime('%d %h %Y')
    
    @property
    def image(self):
        return R("%s.jpg" % self.image_segs['segment'][0].split("@")[0])
        

    # this is the identifier that is passed to download servers
    # it is intended to be one-to-one with posts,
    # but also useful as title for the download on servers

    #@property
    #def identifier(self):
    #    return '%s: %s' % (self.pk, self.title)

    #@classmethod
    #def from_identifier(cls, identifier):
    #    id, title = identifier.split(': ', 1)
    #    try:
    #        return cls.objects.get(id=id)  # , title=title)
    #    except cls.DoesNotExist:
    #        return None

    # methods for extracting the nzb file

    def get_nzb_file(self, connection=None):
        if self.has_encrypted_nzb():
            return StringIO(self.get_encrypted_nzb_content())
        return StringIO(self.get_nzb_content(connection))

    def get_nzb_content(self, connection=None):
        if self.nzb_content is not None:
            return self.nzb_content
        if not connection:
            # create a new connection and close it again
            from Spotnet.Connection import Connection
            connection = Connection(connect=True)
            self.nzb_content = connection.get_nzb(self)
            connection.disconnect()
            return self.nzb_content
        else:
            # leave the connection open
            self.nzb_content = connection.get_nzb(self)
            return self.nzb_content
    
    #https://github.com/michaelw85/spotweb/commit/2b930cb569a83b3c5609bb2ca04cd985b3dda746
    def has_encrypted_nzbsite(self):
        if self.nzb_website:
            return True
        matches = [
            'http://base64.derefer.me',
        ]
        url = None
        if self.website is not None:
            for needle in matches:
                if needle in self.website:
                    url = self.website
                    self.website = "No Website"
        if self.description is not None:
            for needle in matches:
                if needle in self.description:
                    list = re.findall('/\>(%s.*)\</' % re.escape(needle) , self.description)
                    url = list[1]
        if url:
            html = HTTP.Request(url)
            if re.search('meta.+?http-equiv\W+?refresh' , html):
                nzb_url = re.findall('content.+?url\W+?(.+?)\"' , html)
                if len(nzb_url) > 0:
                    self.nzb_website = nzb_url[0]
                    return True
        return False

    def get_encrypted_nzbsite(self):
        if not self.has_encrypted_nzb():
            return False 
        else:
            return self.nzb_website