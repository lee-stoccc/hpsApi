﻿# coding: utf-8

import gevent.monkey

gevent.monkey.patch_all()

import os
import sys
from libs import web
from core.modules.service_modules import import_modules, import_templates
from utils import pyini
from libs.web import render_mako


class Index(object):
    def GET(self):
        return web.seeother('/index')


class StaticFile:
    def GET(self, file):
        f = open('static/' + file)
        return f.read()


def application_init():
    '''应用程序初始化
    '''
    reload(sys)
    sys.setdefaultencoding('utf-8')

    web.config.gevent = True
    web.config.debug = False
    # 初始化基本设置
    web.config.sys = pyini.Ini(os.path.join(os.getcwd(), 'sys_config.ini'))

    web.cache.db = {}
    web.cache.dict = {}

    # mako的渲染
    render = render_mako(
        directories=['templates'],
        input_encoding='utf-8',
        output_encoding='utf-8',
    )

    web.config.render = render

    # 加载应用接口
    # app处理
    app_urls = import_modules(os.path.join(os.getcwd(), 'api'), globals())
    # 静态页面处理
    web_urls = import_templates(os.path.join(os.getcwd(), 'templates'), globals())
    urls = []
    urls.extend(app_urls)
    urls.extend(web_urls)
    urls.extend(['/', Index])
    urls.extend(['/(.*.png|.*.jpg|.*.svg|.*.js|.*.ico|.*.css)', StaticFile])
    app = web.application(urls, globals())

    return app


def init_app_session(webapp):
    '''初始化session
    '''
    web.config.session_parameters['cookie_name'] = 'hps_session_id'
    web.config.session_parameters['cookie_domain'] = None
    web.config.session_parameters['timeout'] = 3600 * 8
    web.config.session_parameters['ignore_expiry'] = False
    web.config.session_parameters['ignore_change_ip'] = True
    web.config.session_parameters['secret_key'] = 'eP2ufxa3efRaIldH0H5J'
    web.config.session_parameters['expired_message'] = '请求会话已经超时， 请重新登陆！'
    web.config.session_parameters['httponly'] = True

    if web.config.get("_session") is None:
        from libs.redis.redis_session import RedisStore
        session = web.session.Session(webapp, RedisStore(ip=web.config.sys.session_redis.server,
                                                         port=web.config.sys.session_redis.port,
                                                         db=web.config.sys.session_redis.db,
                                                         initial_flush=web.config.sys.session_redis.initial_flush),
                                      initializer={'login': False, 'user': None})

        web.config._session = session
    else:
        session = web.config._session

    return session


app = application_init()
session = init_app_session(app)


def session_hook():
    '''session会话设置到上下文
    '''
    web.ctx.session = session


def httphead_loadhook():
    '''加载前http头的设置
    '''
    web.header('Content-type', "text/html; charset=utf-8")
    web.header("Access-Control-Allow-Headers",
               "X-Requested-With,Content-Type,Access-Control-Allow-Origin,Access-Control-Allow-Hearders,X-Requested-By,"
               "Access-Control-Allow-Methods")
    web.header("Access-Control-Allow-Credentials", "true")
    web.header("Access-Control-Allow-Methods", 'POST,GET,PUT,DELETE,OPTIONS')
    # web.header("Access-Control-Allow-Origin", "http://10.3.15.79:4200")
    web.header("Access-Control-Allow-Origin", "http://192.168.1.135:4200")
    # web.header("Access-Control-Allow-Origin", "*")


# 启动程序
app.add_processor(web.loadhook(httphead_loadhook))
app.add_processor(web.loadhook(session_hook))
application = app.wsgifunc()

if __name__ == "__main__":
    web.httpserver.runsimple(app.wsgifunc(), ('0.0.0.0', 8090))
