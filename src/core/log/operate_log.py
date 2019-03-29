# coding: utf-8

from libs import web
from sqlalchemy.sql.expression import text
from core.cc import get_db
from libs.orm.ormutils import dbtranscoped
from utils.func_api import FuncResult
from libs.orm.dbcontext import DBContext
from utils.tools import obj_to_dict, obj_to_json
from datetime import datetime

def get_log(LogInfo):
    # if not web.ctx.get('LogInfo'):
    web.ctx.LogInfo = ''
    # web.ctx.LogInfo.append(LogInfo)
    web.ctx.LogInfo = LogInfo

def init_db(conn):
    '''初始化数据库连接
        Params:
            @conn:数据库连接串
    '''

    try:
        # 如果已经存在一个数据连接则先释放

        release_db()

        # 新建一个数据库连接

        dbcontext = DBContext(conn)
        web.ctx.dbcontext = dbcontext
        web.ctx.cur_dbconn = dbcontext.dbconn
        web.ctx.cur_dbsession = dbcontext.dbsession
        web.ctx.cur_trans_count = 1

        return FuncResult(success=True)

    except Exception, ce:
        return FuncResult(fail='数据库初始化失败!')


def release_db():
    '''释放当前上下文的数据库连接
    '''
    if web.ctx.get('dbcontext') and web.ctx.dbcontext:
        web.ctx.dbcontext.release_db()

def generate_log(objOldValue, objNewValue):
    dictValue = obj_to_dict(objOldValue)
    sLogInfo = ''
    for key in dictValue.keys():
        sOldValue = getattr(objOldValue, key)
        sNewValue = getattr(objNewValue, key)

        if sOldValue != sNewValue:
            if sLogInfo == '':
                sLogInfo = key + ':' + sOldValue + '-->' + sNewValue
            else:
                sLogInfo = sLogInfo + ',' + key + ':' + sOldValue + '-->' + sNewValue
    write_log(sLogInfo)


# def write_operate_log(log_data=None):
#     '''日志记录
#                     需要记录的信息:
#                         日志唯一标记、操作员编号、操作员名称、日志类型、操作内容、ip、操作时间、备注
#     '''
#     try:
#         write_log(log_data)
#
#     except Exception, ce:
#         print ce.message


def write_log(log_data=None):
    try:
        db_cc = get_db()
        if not db_cc:
            return
        init_db(db_cc)

        write_log_db(log_data)
    except Exception, ce:
        print ce.message


@dbtranscoped()
def write_log_db(log_data=None):
    '''写入日志到数据库
    '''

    table_name = 'l_operating_log'

    try:

        sql = '''INSERT INTO `%s` (`UserID`,`WorkCode`,`UserName`,`OperaType`,`LogInfo`,`IP`,`CreateTime`,`Remark`)
            VALUES (:UserID,:WorkCode,:UserName,:OperaType,:LogInfo,:IP,:CreateTime,:Remark)'''

        if web.ctx.session.user:
            nUserID = web.ctx.session.user['UserID']
            sWorkCode = web.ctx.session.user['UserCode']
            sUserName = web.ctx.session.user['UserName']
        else:
            nUserID = ''
            sWorkCode = ''
            sUserName = ''
        if web.input().get('sRemark'):
            sRemark = web.input().get('sRemark')
        else:
            sRemark = ''

        web.ctx.cur_dbconn.execute(text(sql % table_name),
                                   UserID = nUserID,
                                   WorkCode = sWorkCode,
                                   UserName = sUserName,
                                   OperaType = web.ctx.apiDesc if web.ctx.apiDesc else '',
                                   LogInfo = obj_to_json(log_data),
                                   IP = web.ctx.ip,
                                   CreateTime = datetime.now(),
                                   Remark = sRemark)

    except:
        from utils.trace_except import get_cur_except
        print get_cur_except()[0]
        pass


    return FuncResult(success=True)

    