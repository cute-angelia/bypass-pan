#!/usr/bin/python
# coding:utf-8
from aiohttp import web
from sites.yifile import YifileSite
import asyncio

yifile2 = YifileSite('xxxxx', 'xxxx')
loginstatus = yifile2.login()
print ('login', loginstatus)
if loginstatus:
   yifile2.checkJedong()

async def handle_greeting(request):
    name = request.match_info.get('name', "Anonymous")
    txt = "Hello, {}".format(name)
    return web.Response(text=txt)

async def handle_login(request):
    txt = loginstatus = yifile2.login()
    return web.Response(text=txt)

async def handle_download(request):
    postData = await request.post()
    url = postData.get("url")
    code = postData.get("code")
    data = yifile2.download(url, code)
    print ('download', data)
    return web.json_response(data)

async def handle_checkJiedong(request):
    data = yifile2.checkJedong()
    return web.json_response(data)

async def handle_sendJiedongEmail(request):
    data = yifile2.sendJedong()
    return web.json_response(data)

async def handle_code(request):
    data = yifile2.getCode()
    return web.Response(body=data, content_type="image/png")

def run(port=8777):
    app = web.Application()
    app.add_routes([
        web.get('/{name}', handle_greeting),
        web.post('/ali/download', handle_download),
        web.get('/ali/checkJedong', handle_checkJiedong),
        web.get('/ali/login', handle_login),
        web.get('/ali/sendJedong', handle_sendJiedongEmail),
        web.get('/ali/code', handle_code)
    ])
    web.run_app(app, port=port)


if __name__ == "__main__":
    from sys import argv

    port = 8777
    if len(argv) == 2:
        port = int(argv[1])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            run(port)
        )
    )

    
