#!/usr/bin/python
# coding:utf-8
"""
Very simple HTTP server in python.
Usage::
    ./dummy-web-server.py [<port>]
Send a GET request::
    curl http://localhost
Send a HEAD request::
    curl -I http://localhost
Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from sites.yifile import YifileSite
import urlparse
import urllib
import json

yifile2 = YifileSite('a308057848', 'lovetwins')
loginstatus = yifile2.login()
print ('login', loginstatus)
if loginstatus:
   yifile2.checkJedong()


class S(BaseHTTPRequestHandler):
    def do_GET(self):
        result = urlparse.urlparse(self.path)
        self.do_action(result.path, urlparse.parse_qs(result.query))

    def do_POST(self):
        result = urlparse.urlparse(self.path)
        self.do_action(result.path, urlparse.parse_qs(result.query))

        postData = request.post()

        if path == '/ali/download':
            self._set_headers_json()
            url = postData['url']
            code = postData['code']
            #data = yifile2.download(url, code)
            print ('download', url, code)

            self.wfile.write(json.dumps(data))

    def do_action(self, path, args):
        if path == '/ali/login':
            self._set_headers()
            loginstatus = yifile2.login()
            print ('login', loginstatus)
            if loginstatus:
                self.wfile.write(
                    "<html><body><h1>login ok!</h1></body></html>")
            else:
                self.wfile.write(
                    "<html><body><h1>login failed!</h1></body></html>")
        elif path == '/ali/download':
            self._set_headers_json()
            url = args['url'][0]
            code = args['code'][0]
            data = yifile2.download(url, code)
            print ('download', data)

            self.wfile.write(json.dumps(data))
        # 解冻
        elif path == '/ali/checkJedong':
            self._set_headers()
            data = yifile2.checkJedong()
            self.wfile.write(data)
        # 解冻
        elif path == '/ali/sendJedong':
            self._set_headers()
            data = yifile2.sendJedong()
            self.wfile.write(data)
        # do解冻
        elif path == '/ali/doJedong':
            self._set_headers()
            url = args['url'][0]
            data = yifile2.doJedong(url)
            self.wfile.write(data)
        # 验证码
        elif path == '/ali/code':
            self._set_headers_png()
            data = yifile2.getCode()
            self.wfile.write(data)
        else:
            self._set_headers()
            self.wfile.write("<html><body><h1>hi!"+path+"</h1></body></html>")

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _set_headers_png(self):
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()

    def _set_headers_json(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()


def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print ('Starting httpd...')
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
