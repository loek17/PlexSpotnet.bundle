from BaseSettings import Settings

def _(str):
    try:
        str = L(str)
    except:
        pass
    return str

def get(name , fallback):
    try:
        retr = Prefs[name]
    except:
        retr = fallback
    return retr

class ImproperlyConfigured(Exception):
    pass

class SpotSettings(Settings):
    "Setting voor the spotnet part of this plugin"
    
    @staticmethod
    def load():
        pass
    
    SPOTNET_SERVER_HOST = get('SPOTNET_SERVER_HOST' , False)
  
    SPOTNET_SERVER_PORT    = get(  'SPOTNET_SERVER_PORT',            119)
    SPOTNET_SERVER_SSL     = get(  'SPOTNET_SERVER_SSL',             False)
    SERVER_USERNAME        = get(  'SPOTNET_SERVER_USERNAME',        None)
    SERVER_PASSWORD        = get(  'SPOTNET_SERVER_PASSWORD',        None)
    SERVER_READERMODE      = get(  'SPOTNET_SERVER_READERMODE',      False)

    SPOTNET_UPDATE_MAXPOST         = get(  'SPOTNET_UPDATE_MAXPOST',         20000)
    SPOTNET_UPDATE_EXTRA           = get(  'SPOTNET_UPDATE_EXTRA',           15000)
    SPOTNET_UPDATE_BULK_COUNT      = get(  'SPOTNET_UPDATE_BULK_COUNT',      1000)
    SPOTNET_UPDATE_GROUPS          = get(  'SPOTNET_UPDATE_GROUPS',          ('free.pt', 'spot.net', ))
    UPDATE_COMMENT_GROUPS          = get(  'SPOTNET_UPDATE_COMMENT_GROUPS',  ('free.usenet', ))
    UPDATE_DISCARD_ENDINGS         = get(  'SPOTNET_UPDATE_DISCARD_ENDINGS', (SPOTNET_SERVER_HOST,))

    MAX_CONNECTIONS        = int(get("MAX_CONNECTIONS" ,             3))    
    MAX_AGE                = get(  'MAX_AGE' ,                       31)
    UPDATE_ON_BOOT         = get(  'SPOTNET_UPDATE_ON_BOOT',         False)
    CLEANUP_MINAGE         = get(  'SPOTNET_CLEANUP_MINAGE',         1999)
    POST_PER_PAGE          = get(  'SPOTNET_POST_PER_PAGE',          30)
    KEEP_PRON              = get(  'KEEP_PRON' ,                     False)

    POST_DB                = None
    FILTER_DB              = None
    ROOT_PATH              = None
    IMAGE_DIR              = None
    DB_DIR                 = None

    DEFAULT_FILTERS = get( 'SPOTNET_DEFAULT_FILTERS' , [
        {
            "name" : "Films",
            "description" : "Filter for films",
            "category_code" : 1,
            "subcategory_codes" : {
                "z" : [0]
            },
            "porn" : False
        },
        {
            "name" : "Series",
            "description" : "Filter for Series",
            "category_code" : 1,
            "subcategory_codes" : {
                "z" : [1]
            },
            "porn" : False
        },
        {
            "name" : "Album",
            "description" : "Filter for albums",
            "category_code" : 2,
            "subcategory_codes" : {
                "z" : [0]
            },
            "porn" : False
        },
        {
            "name" : "Podcast",
            "description" : "Filter for Podcast",
            "category_code" : 2,
            "subcategory_codes" : {
                "z" : [2]
            },
            "porn" : False
        },
        {
            "name" : "mp3",
            "description" : "Filter for mp3",
            "category_code" : 2,
            "subcategory_codes" : {
                "a" : [0]
            },
            "porn" : False
        },
        {
            "name" : "Windows",
            "description" : "Filter for Windows games",
            "category_code" : 3,
            "subcategory_codes" : {
                "a" : [0]
            },
            "porn" : False
        },
        {
            "name" : "Windows",
            "description" : "Filter for Windows aplications",
            "category_code" : 4,
            "subcategory_codes" : {
                "a" : [0]
            },
            "porn" : False
        },
    ])

    CATEGORY_MAPPING = get(  'SPOTNET_CATEGORY_MAPPING', {
        1: _('image'),
        2: _('sound'),
        3: _('game'),
        4: _('application'),
    })
    CATEGORY_REVERSED_MAPPING = dict((v, k) for k, v in CATEGORY_MAPPING.iteritems())

    SUBCATEGORY_TYPE_MAPPING = get(  'SPOTNET_SUBCATEGORY_TYPE_MAPPING', {
        1: dict(
            a=_('format'),
            b=_('source'),
            c=_('language'),
            d=_('genre'),
            z=_('type'),
        ),
        2: dict(
            a=_('format'),
            b=_('source'),
            c=_('bitrate'),
            d=_('genre'),
            z=_('type'),
        ),
        3: dict(
            a=_('platform'),
            b=_('format'),
            c=_('genre'),
        ),
        4: dict(
            a=_('platform'),
            b=_('genre'),
        ),
    })

    SUBCATEGORY_MAPPING = get('SPOTNET_SUBCATEGORY_MAPPING', {
        # source: https://github.com/spotweb/spotweb/blob/master/lib/SpotCategories.php
        1: dict(
            a={
                0: _('DivX'),
                1: _('wmv'),
                2: _('mpg'),
                3: _('dvd5'),
                4: _('other highdef'),
                5: _('ePub'),
                6: _('Blu-ray'),
                7: _('hd-dvd'),
                8: _('wmvhd'),
                9: _('x264hd'),
                10: _('dvd9'),
            },
            b={
                0: _('cam'),
                1: _('(s)vcd'),
                2: _('promo'),
                3: _('retail'),
                4: _('tv'),
                #5: _(''),
                6: _('satellite'),
                7: _('r5'),
                8: _('telecine'),
                9: _('telesync'),
                10: _('scan'),
            },
            c={
                0: _('no subtitles'),
                1: _('dutch subtitled (external)'),
                2: _('dutch subtitled (internal)'),
                3: _('english subtitled (external)'),
                4: _('english subtitled (internal)'),
                #5: _(''),
                6: _('dutch subtitled (selectable)'),
                7: _('english subtitled (selectable)'),
                #8: _(''),
                #9: _(''),
                10: _('english spoken'),
                11: _('dutch spoken'),
                12: _('german spoken'),
                13: _('french spoken'),
                14: _('spanish spoken'),
            },
            d={
                0: _('action'),
                1: _('adventure'),
                2: _('animation'),
                3: _('cabaret'),
                4: _('comedy'),
                5: _('crime'),
                6: _('documentary'),
                7: _('drama'),
                8: _('family'),
                9: _('fantasy'),
                10: _('art film'),
                11: _('television'),
                12: _('horror'),
                13: _('music'),
                14: _('musical'),
                15: _('mystery'),
                16: _('romance'),
                17: _('science fiction'),
                18: _('sport'),
                19: _('short movie'),
                20: _('thriller'),
                21: _('war'),
                22: _('western'),
                23: _('erotica (hetero)'),
                24: _('erotica (gay men)'),
                25: _('erotica (gay women)'),
                26: _('erotica (bi)'),
                #27: _(''),
                28: _('asian'),
                29: _('anime'),
                30: _('cover'),
                31: _('comic'),
                '-32': _('cartoon'),    # DUPLICATE!
                32: _('study'),
                '-33': _('kids'),       # DUPLICATE!
                33: _('business'),
                34: _('economics'),
                35: _('computer'),
                36: _('hobby'),
                37: _('cooking'),
                38: _('crafts'),
                39: _('handwork'),
                40: _('health'),
                41: _('history'),
                42: _('psychology'),
                43: _('journal'),
                44: _('magazine'),
                45: _('science'),
                46: _('women'),
                47: _('religion'),
                48: _('novel'),
                49: _('biography'),
                50: _('detective'),
                51: _('animals'),
                52: _('humor'),
                53: _('travel'),
                54: _('true events'),
                55: _('nonfiction'),
                56: _('politics'),
                57: _('poetry'),
                58: _('fairy tale'),
                59: _('technics'),
                60: _('art'),
                #61 - 71
                72: _('bi'),
                73: _('lesbian'),
                74: _('gay'),
                75: _('hetero'),
                76: _('amature'),
                77: _('group'),
                78: _('pov'),
                79: _('solo'),
                80: _('young'),
                81: _('soft'),
                82: _('fetish'),
                83: _('old'),
                84: _('fat'),
                85: _('sm'),
                86: _('rough'),
                87: _('dark'),
                88: _('hentai'),
                89: _('outside'),
            },
            z={
                0: _('movie'),
                1: _('series'),
                2: _('book'),
                3: _('erotica'),
            },
        ),
        2: dict(
            a={
                0: _('mp3'),
                1: _('wma'),
                2: _('wav'),
                3: _('ogg'),
                4: _('eac'),
                5: _('dts'),
                6: _('aac'),
                7: _('ape'),
                8: _('flac'),
            },
            b={
                0: _('cd'),
                1: _('radio'),
                2: _('compilation'),
                3: _('dvd'),
                #4: _(''),
                5: _('vinyl'),
                6: _('stream'),
            },
            c={
                0: _('variable'),
                1: _('< 96k'),
                2: _('96k'),
                3: _('128k'),
                4: _('160k'),
                5: _('192k'),
                6: _('256k'),
                7: _('320k'),
                8: _('lossless'),
                #9: _(''),
            },
            d={
                0: _('blues'),
                1: _('compilation'),
                2: _('cabaret'),
                3: _('dance'),
                4: _('various'),
                5: _('hardcore'),
                6: _('world'),
                7: _('jazz'),
                8: _('kids'),
                9: _('classic'),
                10: _('preforming'),
                11: _('dutch'),
                12: _('new age'),
                13: _('pop'),
                14: _('r&b'),
                15: _('hiphop'),
                16: _('reggae'),
                17: _('religious'),
                18: _('rock'),
                19: _('soundtrack'),
                #20: _(''),
                21: _('hardstyle'),
                22: _('asian'),
                23: _('disco'),
                24: _('classics'),
                25: _('metal'),
                26: _('country'),
                27: _('dubstep'),
                28: _('dutch hiphop'),
                29: _('drum&bass'),
                30: _('electro'),
                31: _('folk'),
                32: _('soul'),
                33: _('trance'),
                34: _('balkan'),
                35: _('techno'),
                36: _('ambient'),
                37: _('latin'),
                38: _('live'),
            },
            z={
                0: _('album'),
                1: _('liveset'),
                2: _('podcast'),
                3: _('audiobook'),
            },
        ),
        3: dict(
            a={
                0: _('windows'),
                1: _('mac'),
                2: _('unix'),
                3: _('ps'),
                4: _('ps2'),
                5: _('psp'),
                6: _('xbox'),
                7: _('360'),
                8: _('gba'),
                9: _('gc'),
                10: _('nds'),
                11: _('Wii'),
                12: _('ps3'),
                13: _('windows phone'),
                14: _('iOS'),
                15: _('android'),
                16: _('3ds'),
            },
            b={
                0: _('iso'),
                1: _('rip'),
                2: _('retail'),
                3: _('dlc'),
                #4: _(''),
                5: _('patch'),
                6: _('crack'),
            },
            c={
                0: _('action'),
                1: _('adventure'),
                2: _('strategy'),
                3: _('roleplay'),
                4: _('simulation'),
                5: _('race'),
                6: _('flying'),
                7: _('shooter'),
                8: _('platform'),
                9: _('sport'),
                10: _('kids'),
                11: _('puzzle'),
                #12: _(''),
                13: _('bordgame'),
                14: _('cards'),
                15: _('education'),
                16: _('music'),
                17: _('family'),
            },
        ),
        4: dict(
            a={
                0: _('windows'),
                1: _('mac'),
                2: _('unix'),
                3: _('os/2'),
                4: _('windows phone'),
                5: _('nav'),
                6: _('iOS'),
                7: _('android'),
            },
            b={
                0: _('audio'),
                1: _('video'),
                2: _('graphics'),
                3: _('cd/dvd tools'),
                4: _('media players'),
                5: _('rippers & encoders'),
                6: _('plugins'),
                7: _('database tools'),
                8: _('email software'),
                9: _('picture managers'),
                10: _('screensavers'),
                11: _('skins'),
                12: _('drivers'),
                13: _('browsers'),
                14: _('download managers'),
                15: _('download'),
                16: _('usenet software'),
                17: _('rss readers'),
                18: _('ftp software'),
                19: _('firewalls'),
                20: _('antivirus'),
                21: _('antispyware'),
                22: _('optimization software'),
                23: _('security software'),
                24: _('system software'),
                #25: _(''),
                26: _('educational'),
                27: _('office'),
                28: _('internet'),
                29: _('communication'),
                30: _('development'),
                31: _('spotnet'),
            },
        ),
    })


    # spot verification keys
    VERIFICATION_KEYS = get(  'SPOTNET_VERIFICATION_KEYS', (
        # default verification keys from:
        '',
    ))

    #update the main setting



