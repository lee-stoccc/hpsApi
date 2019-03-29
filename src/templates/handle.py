# coding: utf-8
'''
Created on 2013-11-12

@author: Administrator
'''
import os
from libs import web
 

class handler(object):      
    def GET(self):
        #如果没登录则跳转到登录界面
        # print 'cookie', web.cookies().get('userInfo')
        if web.ctx.path.split('/')[-1:][0] != 'index' and not web.ctx.session.login:
            raise web.seeother('/index')
    
        if hasattr(web.config.render, web.ctx.path):
            return getattr(web.config.render, web.ctx.path)()
        else: 
            return web.notfound("Sorry, the page you were looking for was not found.")