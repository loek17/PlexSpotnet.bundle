import nntplib
import socket
import errno
import sys

import zlib
import io
                                #misschien beter
from cStringIO import StringIO    #now using

import Settings
from Post import RawPost, InvalidPost , Post
from Decode import decode_nzb, DecodeNzbError , decode_image

# TODO:
# maybe decode headers using a function (new in python 3?)
# http://docs.python.org/py3k/library/nntplib.html?highlight=nntp#nntplib.decode_header

NEWSSERVER_UNAUTH_USERNAME = None
NEWSSERVER_UNAUTH_PASSWORD = None


class ConnectionError(Exception):
    pass


class ConnectError(ConnectionError):
    pass


class NotFoundError(Exception):
    pass


#
# We are working with two types of id's here
#
# - messageid : universally unique id, eg: '<3ae6b2dcccdf42988a85dc314370ba0123@free.pt>'
# - postnumber : server dependent id, eg: '65903' (always use strings in nntplib!)
#


class Connection(object):
    """Class to connect to the nntp server with."""

    def __init__(self, db ,connect=True):
        self.nntp = None
        self.db = db
        if connect:
            self.connect()

    # public methods

    def is_connected(self):
        return self.nntp is not None

    def connect(self):
        # connect to server
        try:
            if sys.version[:2] < (3, 2):
                nntp = nntplib.NNTP(
                    host=Settings.SPOTNET_SERVER_HOST,
                    port=Settings.SPOTNET_SERVER_PORT,
                    user=(
                        Settings.SERVER_USERNAME
                        if Settings.SERVER_USERNAME is not None
                        else NEWSSERVER_UNAUTH_USERNAME
                    ),
                    password=(
                        Settings.SERVER_PASSWORD
                        if Settings.SERVER_PASSWORD is not None
                        else NEWSSERVER_UNAUTH_PASSWORD
                    ),
                    readermode=Settings.SERVER_READERMODE,
                    usenetrc=False,
                )
            else:
                # try to encrypt connection using ssl(only for python 3.2+)
                nntp = nntplib.NNTP(
                    host=Settings.SPOTNET_SERVER_HOST,
                    port=Settings.SPOTNET_SERVER_PORT,
                    readermode=Settings.SERVER_READERMODE,
                    usenetrc=False,
                )
                # this 'starttls' method is introduced in python 3.2
                nntp.starttls(ssl_context=None)
                # login, now that we might be encrypted
                nntp.login(
                    user=Settings.SERVER_USERNAME if Settings.SERVER_USERNAME is not None else NEWSSERVER_UNAUTH_USERNAME,
                    password=Settings.SERVER_PASSWORD if Settings.SERVER_PASSWORD is not None else NEWSSERVER_UNAUTH_PASSWORD,
                )
        except (nntplib.NNTPError, socket.error) as e:
            raise ConnectError(e)
        self.nntp = nntp

    def disconnect(self):
        if self.is_connected():
            try:
                quitmsg = self.nntp.quit()
            except EOFError:
                # seems to happen for me, but we're still disconnected
                # TODO: find a way to check if we're really disconnected
                # and rethrow the exception if not
                pass
            except socket.error as e:
                if e.errno != errno.EPIPE:
                    raise
            self.nntp = None

    def update(self, logger=Log.Info):
        "Retrieves all new posts."
        logger("Updating spotnet")

        self.db.db.open()
        self.db.open = True

        for group in Settings.SPOTNET_UPDATE_GROUPS:
            self.update_group(group, logger)
        Log.Info('done updating database')

        self.db.db.close()
        self.db.open = False

        Log.Info('start cleaning up')
        self.db.cleanup()
        Log.Info('done cleaning up')

    # private update methods

    def update_group(self, groupname, logger=Log.Info):
        logger("Updating group '%s'" % groupname)
        try:
            gresp = self.nntp.group(groupname)
        except (nntplib.NNTPError, socket.error) as e:
            logger("Failed updating group '%s': %s" % (groupname, e))
            return ConnectionError(e)

        first_on_server, last = gresp[2], gresp[3]  # first < last
        last_in_db = self.get_last_postnumber_in_db()    # solved

        first_options = [int(first_on_server)]
        if last_in_db is not None:
            first_options.append(int(last_in_db))
        if Settings.SPOTNET_UPDATE_MAXPOST is not None:
            first_options.append(int(last) - int(Settings.SPOTNET_UPDATE_MAXPOST))
        first = max(first_options)
        last = int(last)
        
        Log.Info(" we are starting with %d and ending with %d" % (first , last))
        
        curstart = first
        last_added = None
        while curstart < last + int(Settings.SPOTNET_UPDATE_EXTRA):
            x = self.update_group_postnumbers(
                groupname,
                curstart,
                curstart + int(Settings.SPOTNET_UPDATE_BULK_COUNT),
                logger,
            )
            if x:
                last_added = x
            curstart += int(Settings.SPOTNET_UPDATE_BULK_COUNT)

        # store last added post's postnumber
        # since there's not always a way to obtain it
        # from the last messageid alone
        if Settings.UPDATE_LAST_STORAGE:
            self.set_last_postnumber_in_db(last_added)

    def update_group_postnumbers(self, groupname, start, end, logger=Log.Info):
        logger("Updating group '%s', block [%d, %d]" % (groupname, start, end))
        try:
            xover = self.nntp.xover(str(start), str(end))
        except (nntplib.NNTPError, socket.error) as e:
            logger(
                "Error updating group '%s', block [%d, %d]: %s"
                % (groupname, start, end, e)
            )
            if '430' in str(e):
                return False
            #raise ConnectionError(e)
            raise e
        last_added = None
        index = 0
        self.noop = Thread.CreateTimer(30.0 , self.send_noop)
        while index < len(xover[1]):
            post = xover[1][index]
            
            #prevent time out
            self.noop.cancel()
            self.noop = Thread.CreateTimer(30.0 , self.send_noop)
            
            # we limit ourselves here since not all posts
            # seem to provide real spotnet posts
            if post[4][:-1].split('@', 1)[-1] not in Settings.UPDATE_DISCARD_ENDINGS:
                if not self.db.db.select(['messageid'] , messageid=post[4]):
                    try:
                        if self.add_post(
                            post[0],
                            post[4],
                            logger,
                        ):
                            last_added = post[0]
                    except socket.error as e:
                        if e.errno == errno.ECONNRESET:
                            # this happens, just reconnect and proceed
                            self.disconnect()
                            self.connect()
                            index -= 1
                        else:
                            raise
            #else:
            #    if self.add_post(post[0], post[4]):
            #        raise Exception("Discarded real post!")
            index += 1
        self.noop.cancel()
        return last_added

    def get_post_header(self, header, post):
        index = 0
        h = '%s: ' % header
        while not post[3][index].startswith(h) and index < len(post[3]):
            index += 1
        assert post[3][index].startswith(h), \
            "Post %s does not have a '%s' header!" % (post[2], header)
        return post[3][index][len(h):]

    def add_post(self, postnumber, messageid, logger=Log.Info):
        "Add a new post to the database (not post a new post)"
        try:
            post = self.nntp.article(messageid)
        except (nntplib.NNTPError, socket.error) as e:
            # TODO: don't give up so easily
            logger("failed to add post, networkt error ,  " + messageid)
            return False
        except EOFError as e:
            logger("we where disconnected we reconnect now")
            self.disconnect()
            self.connect()
            return self.add_post(self, postnumber, messageid, logger=Log.Info)
        # check for dispose messages
        subject = self.get_post_header('Subject', post)
        if subject.startswith('DISPOSE '):  # and '@' in subject:
            # it's a dispose message
            dispose = subject[len('DISPOSE '):]
            dispose_messageid , dispose_title = dispose.split(' - ' , 1)
            try:
                logger("post is dispose post messageid = %s , title = %s we are deleting it" % (dispose_messageid , dispose_title))
            except UnicodeDecodeError:
                pass
            self.db.del_post_form_database('<%s>' % dispose_messageid)
            return False
        # if this isn't a dispose message, add it as a real post
        try:
            newpost = Post()
            newpost.form_rawpost(RawPost(postnumber, post))
        except InvalidPost as e:
            logger("Skipped invalid post %s: %s" % (postnumber, e))
            return False
        # check if the user wants to keep this post
        if not Settings.KEEP_PRON and newpost.is_porn():
            return False
        self.db.add_post_to_database(newpost)
        # maby check if message id is unique // done is add_post_to_database
        # get image and save it
        if newpost.has_image():
            try:
                self.get_image(newpost.image_segs['segment'])
            except (NotFoundError , EOFError):
                pass
            except:
                raise
        return True

    def send_noop(self):
        self.nntp.help()
        self.noop = Thread.CreateTimer(30.0 , self.send_noop)

    def get_raw_post(self, messageid):
        try:
            post = self.nntp.article(messageid)
        except (nntplib.NNTPError, socket.error) as e:
            raise ConnectionError(e)
        else:
            return RawPost(None, post)  # TODO: maybe we do need the postnumber

    def verify_post(self, post):
        keys = Settings.VERIFICATION_KEYS
        if keys is None or len(keys) == 0:
            return True
        else:
            raise NotImplementedError  # TODO

    # public functionality methods

    def get_nzb(self, post):
        "Retrieves the nzb for a post, returned is the nzb content"
        assert self.is_connected()
        zipped = StringIO()  # TODO: maybe replace this with os.tmpfile
        try:
            for messageid in post.nzb:
                self.nntp.body('<%s>' % messageid, zipped)
        except nntplib.NNTPTemporaryError as e:
            if e.response == '430 No such article':
                raise NotFoundError
            else:
                raise
        content = zipped.getvalue()
        del zipped

        try:
            return decode_nzb(content)
        except DecodeNzbError as e:
            raise ConnectionError(e.msg)

    def get_image(self , image_segs):
        "download the image for a spot"
        assert self.is_connected()

        content = ''
        try:
            for messageid in image_segs:                                # this doesn't work for image witch are devided in multiple segments but this rarely happens.
                tmp = ''.join(self.nntp.body('<%s>' % messageid)[3])
                content = content + decode_image(tmp)
        except nntplib.NNTPTemporaryError as e:
            if e.response == '430 No such article':
                raise NotFoundError
            else:
                raise

        image = io.open(Settings.IMAGE_DIR % image_segs[0].split("@")[0] , 'wb')
        image.write(content)
        image.close()

        return "%s.jpg" % image_segs[0].split("@")[0]

    def get_comments(self, post):
        "Retrieves the comments for a post"
        assert self.is_connected()
        raise NotImplementedError  # TODO

    # internal utility methods

    def get_last_messageid_in_db(self):
        try:
            snp = self.db.db.select(['messageid' , 'posted']).sort_by('-posted')[0]        #get the last post id
        except IndexError:
            return None
        else:
            return snp.messageid

    def get_last_postnumber_in_db(self):
        # to be server independend,
        # we get the last messageid
        # and then get the corresponding
        # postnumber
        messageid = self.get_last_messageid_in_db()
        if messageid is None:
            return None
        try:
            stat = self.nntp.stat(messageid)
        except (nntplib.NNTPError, socket.error) as e:
            return None
        else:
            if str(stat[1]) == str(0):
                try:
                   snp = self.db.db.select(['postnumber' , 'posted']).sort_by('-posted')[0]
                except:
                    return None
                else:
                    return snp.postnumber
            else:
                return stat[1]

    def set_last_postnumber_in_db(self, last_added):
        if Settings.UPDATE_LAST_STORAGE:
            raise NotImplementedError