# coding: utf-8
from core.log.operate_log import write_log
from libs import web
from utils.func_api import FuncResult


def write_operate_log():
    if web.ctx.get('LogInfo'):
        #记录业务日志
        # for sLog in web.ctx.lsLog:
        write_log(web.ctx.LogInfo)

    return FuncResult(success=True)