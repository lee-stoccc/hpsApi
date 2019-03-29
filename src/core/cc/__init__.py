# coding: utf-8
import os
from libs import web
from utils import pyini
from utils.crypt import des_encrypt, des_decrypt

web.config.sys = pyini.Ini(os.path.join(os.getcwd(), 'sys_config.ini'))
def get_db():
    #如果已登录，则从session中获取连接信息
    if web.ctx.session.get('login') and web.ctx.session.user.get('dbcc_mysql'):
        return des_decrypt(web.ctx.session.user['dbcc_mysql'], key='hps_dbconn')

    # 设置连接信息，若登录成功，则将连接信息设置session中
    conn = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (web.config.sys.db.user, web.config.sys.db.pwd, web.config.sys.db.server, web.config.sys.db.port, web.config.sys.db.db)
    if web.ctx.session.get('login'):
        web.ctx.session.user['dbcc_mysql'] = des_encrypt(conn, key='hps_dbconn')
    return conn
