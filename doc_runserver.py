from livereload import Server
from sphinx_autobuild.__init__ import LivereloadWatchdogWatcher
from django.contrib.auth.decorators import login_required
from livereload.handlers import LiveReloadHandler, MtimeStaticFileHandler
from livereload.server import LiveScriptInjector, LiveScriptContainer
import os

import tornado
from tornado import web
from tornado import escape

from django.conf import settings

import base64
import functools

# API_KEYS = {
#     'rjtzWc674hDxTSWulgETRqHrVVQoI3T8f9RoMlO6zsQ': 'test'
# }
#
#
# def api_auth(username, password):
#     if username in API_KEYS:
#         return True
#     return False
#
#
# def basic_auth(auth):
#     print('basic auth')
#     def decore(f):
#         def _request_auth(handler):
#             print('set header')
#             handler.set_header('WWW-Authenticate', 'Basic realm=JSL')
#             handler.set_status(401)
#             handler.finish()
#             return False
#
#         @functools.wraps(f)
#         def new_f(*args):
#             handler = args[0]
#
#             auth_header = handler.request.headers.get('Authorization')
#             print(auth_header, 'auth_header')
#             if auth_header is None:
#                 return _request_auth(handler)
#             if not auth_header.startswith('basic '):
#                 return _request_auth(handler)
#
#             auth_decoded = base64.b64decode(auth_header[6:]).decode('ascii')
#             username, password = str(auth_decoded).split(':', 1)
#             # auth_decoded = base64.decodestring(auth_header[6:])
#             # username, password = auth_decoded.split(':', 2)
#
#             if (auth(username, password)):
#                 f(*args)
#             else:
#                 print('no auth')
#                 _request_auth(handler)
#
#         return new_f
#
#     return decore
#
#
import livereload
class LiveReloadJSHandler(web.RequestHandler):
    # @tornado.web.authenticated
    # @basic_auth
    def get(self):
        self.set_header('Content-Type', 'application/javascript')
        # root = os.path.abspath(os.path.dirname(__file__))
        root = os.path.dirname(livereload.__file__)
        js_file = os.path.join(root, 'vendors/livereload.js')
        with open(js_file, 'rb') as f:
            self.write(f.read())


class ForceReloadHandler(web.RequestHandler):
    # @tornado.web.authenticated
    # @basic_auth
    def get(self):
        path = self.get_argument('path', default=None) or '*'
        LiveReloadHandler.reload_waiters(path)
        self.write('ok')



# import tornado.httputil
from tornado import httputil
from tornado import iostream
# from tornado.util import (ObjectDict, raise_exc_info,
#                           unicode_type, _websocket_mask, PY3)

# url = URLSpec

# if PY3:
#     import http.cookies as Cookie
#     import urllib.parse as urlparse
#     from urllib.parse import urlencode
# else:
#     import Cookie
#     import urlparse
#     from urllib import urlencode
# from tornado.web import HTTPError
# @tornado.web.authenticated
def authenticated(method):
    """Decorate methods with this to require that the user be logged in.

    If the user is not logged in, they will be redirected to the configured
    `login url <RequestHandler.get_login_url>`.

    If you configure a login url with a query parameter, Tornado will
    assume you know what you're doing and use it as-is.  If not, it
    will add a `next` parameter so the login page knows where to send
    you once you're logged in.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        # if not self.current_user:
        if self.request.method in ("GET", "HEAD"):
            # print('self.request.method in ("GET", "HEAD"):')
            url = self.get_login_url()
            # print(urlparse.urlsplit(url).scheme, url)
            # next_url = self.request.uri
            secure = self.get_secure_cookie("user")
            # print(secure)
            if secure and secure.decode("utf-8") == 'demo':
                # print('try next', next_url, str(secure))
                # self.redirect(next_url)
                # return
                return method(self, *args, **kwargs)
            else:
                # print('not try ', url, str(secure), )
                self.redirect(url)
                return
            # print(next_url, self.get_secure_cookie("user"))
            # print(self.get_secure_cookie("user"))
            # if "?" not in url:
                # if urlparse.urlsplit(url).scheme:
                #     # if login url is absolute, make next absolute too
                #     next_url = self.request.full_url()
                # else:
                #     next_url = self.request.uri
                # url += "?" + urlencode(dict(next=next_url))
            # self.redirect(url)
            # return
        # raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper

class StaticFileHandler(MtimeStaticFileHandler):
    
    # # @tornado.web.authenticated
    # @authenticated
    # @tornado.gen.coroutine
    # def get(self, path, include_body=True):
    #     # Set up our path instance variables.
    #     self.path = self.parse_url_path(path)
    #     del path  # make sure we don't refer to path instead of self.path again
    #     absolute_path = self.get_absolute_path(self.root, self.path)
    #     self.absolute_path = self.validate_absolute_path(
    #         self.root, absolute_path)
    #     if self.absolute_path is None:
    #         return
    #
    #     self.modified = self.get_modified_time()
    #     self.set_headers()
    #
    #     if self.should_return_304():
    #         self.set_status(304)
    #         return
    #
    #     request_range = None
    #     range_header = self.request.headers.get("Range")
    #     if range_header:
    #         # As per RFC 2616 14.16, if an invalid Range header is specified,
    #         # the request will be treated as if the header didn't exist.
    #         request_range = httputil._parse_request_range(range_header)
    #
    #     size = self.get_content_size()
    #     if request_range:
    #         start, end = request_range
    #         if (start is not None and start >= size) or end == 0:
    #             # As per RFC 2616 14.35.1, a range is not satisfiable only: if
    #             # the first requested byte is equal to or greater than the
    #             # content, or when a suffix with length 0 is specified
    #             self.set_status(416)  # Range Not Satisfiable
    #             self.set_header("Content-Type", "text/plain")
    #             self.set_header("Content-Range", "bytes */%s" % (size,))
    #             return
    #         if start is not None and start < 0:
    #             start += size
    #         if end is not None and end > size:
    #             # Clients sometimes blindly use a large range to limit their
    #             # download size; cap the endpoint at the actual file size.
    #             end = size
    #         # Note: only return HTTP 206 if less than the entire range has been
    #         # requested. Not only is this semantically correct, but Chrome
    #         # refuses to play audio if it gets an HTTP 206 in response to
    #         # ``Range: bytes=0-``.
    #         if size != (end or size) - (start or 0):
    #             self.set_status(206)  # Partial Content
    #             self.set_header("Content-Range",
    #                             httputil._get_content_range(start, end, size))
    #     else:
    #         start = end = None
    #
    #     if start is not None and end is not None:
    #         content_length = end - start
    #     elif end is not None:
    #         content_length = end
    #     elif start is not None:
    #         content_length = size - start
    #     else:
    #         content_length = size
    #     self.set_header("Content-Length", content_length)
    #
    #     if include_body:
    #         content = self.get_content(self.absolute_path, start, end)
    #         if isinstance(content, bytes):
    #             content = [content]
    #         for chunk in content:
    #             try:
    #                 self.write(chunk)
    #                 yield self.flush()
    #             except iostream.StreamClosedError:
    #                 return
    #     else:
    #         assert self.request.method == "HEAD"
    #
    #@basic_auth
    # @tornado.web.authenticated
    @authenticated
    def should_return_304(self):
        # print('We there!')
        return False

from tornado import gen
class LoginHandler(web.RequestHandler):
    
    def get_current_user(self):
        return self.get_secure_cookie("user")
    
    # @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        incorrect = self.get_secure_cookie("incorrect")
        if incorrect and int(incorrect) > 20:
            self.write('<center>blocked</center>')
            return
        self.render('login.html')
        # self.render('<html><head><title>Please Log In</title></head>'
        #        '<body><form action="/login" method="POST">'
        #        '<p>Username: <input type="text" name="username" /><p>'
        #        '<p>Password: <input type="password" name="password" /><p>'
        #        '<p><input type="submit" value="Log In" /></p>'
        #        '{% module xsrf_form_html() %}'
        #        '</form></body></html>')
        # return
    

    # self.render('login.html')

    @tornado.gen.coroutine
    def post(self):
        incorrect = self.get_secure_cookie("incorrect")
        if incorrect and int(incorrect) > 20:
            self.write('<center>blocked</center>')
            return
    
        getusername = tornado.escape.xhtml_escape(self.get_argument("username"))
        getpassword = tornado.escape.xhtml_escape(self.get_argument("password"))
        if "demo" == getusername and "demo" == getpassword:
            self.set_secure_cookie("user", self.get_argument("username"))
            self.set_secure_cookie("incorrect", "0")
            
            self.redirect(u"/", permanent=True)
            # self.redirect(self.reverse_url("main"))
        else:
            incorrect = self.get_secure_cookie("incorrect") or 0
            increased = str(int(incorrect) + 1)
            self.set_secure_cookie("incorrect", increased)
            self.write("""<center>
                                Something Wrong With Your Data (%s)<br />
                                <a href="/">Go Home</a>
                              </center>""" % increased)


class ServerSpecific(Server):
    def get_web_handlers(self, script):
        print(self.root)
        if self.app:
            fallback = LiveScriptContainer(self.app, script)
            return [(r'.*', web.FallbackHandler, {'fallback': fallback})]
        return [
            (r'/(.*)', StaticFileHandler, {
                'path': self.root or '.',
                'default_filename': 'index.html',
            }),
        ]
    
    def application(self, port, host, liveport=None, debug=None,
                    live_css=True):
        LiveReloadHandler.watcher = self.watcher
        LiveReloadHandler.live_css = live_css
        if debug is None and self.app:
            debug = True
        
        live_handlers = [
            (r'/livereload', LiveReloadHandler),
            (r'/forcereload', ForceReloadHandler),
            (r'/livereload.js', LiveReloadJSHandler),
            (r"/login", LoginHandler),
        ]
        
        # The livereload.js snippet.
        # Uses JavaScript to dynamically inject the client's hostname.
        # This allows for serving on 0.0.0.0.
        live_script = (
            '<script type="text/javascript">(function(){'
            'var s=document.createElement("script");'
            'var port=%s;'
            's.src="//"+window.location.hostname+":"+port'
            '+ "/livereload.js?port=" + port;'
            'document.head.appendChild(s);'
            '})();</script>'
        )
        if liveport:
            live_script = escape.utf8(live_script % liveport)
        else:
            live_script = escape.utf8(live_script % 'window.location.port')
        
        web_handlers = self.get_web_handlers(live_script)
        
        class ConfiguredTransform(LiveScriptInjector):
            script = live_script
        
        settings = {
            "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
            "login_url": "/login",
            'template_path': os.path.join(os.path.dirname(__file__), "templates"),
            'static_path': os.path.join(os.path.dirname(__file__), "static"),
            # 'debug': True,
            "xsrf_cookies": True
        }
        
        if not liveport:
            handlers = live_handlers + web_handlers
            app = web.Application(
                handlers=handlers,
                debug=debug,
                transforms=[ConfiguredTransform],
                **settings,
            )
            app.listen(port, address=host)
        else:
            app = web.Application(
                handlers=web_handlers,
                debug=debug,
                transforms=[ConfiguredTransform]
            )
            app.listen(port, address=host)
            live = web.Application(handlers=live_handlers, debug=False)
            live.listen(liveport, address=host)


# settings.configure
# print(settings.SECRET_KEY, vars(settings))
# import livereload
# import os
# path = os.path.abspath(livereload.__file__)
# dirr = os.path.dirname(livereload.__file__)
# print(path, dirr)
server = ServerSpecific(
    watcher=LivereloadWatchdogWatcher(use_polling=True),
    # path=path
)

server.serve(port=8080, host='0.0.0.0',
             root='documentation/_build', open_url_delay=0)
