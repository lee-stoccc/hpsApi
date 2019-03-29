# coding: utf-8
'''
Created on 2012-8-22

@author: lill
'''
import collections
import functools
from datetime import datetime
from libs import web  
from tools import obj_to_json


 
class FuncResult(object):
    '''函数调用返回结果对象， 用于判断函数调用的状态
    '''   
    def __init__(self, success=False, fail=None, data=None, msg=None, fail_type=None):
        '''对象初始化
            Params:
                @success:调用返回状态， if True 则data=调用成功结果 else fail,msg=调用失败结果
                @fail:调用失败结果（开发）
                @data:调用成功结果
                @msg:调用失败结果(用户)
                @fail_type:失败类型
        '''
        self.success = success
        self.fail = fail
        self.data = data
        self.msg = msg
        self.fail_type = fail_type
        #code:错误编码, desc:错误的友好显示， 
        #level:错误的级别 , error:真正的异常信息
        #static Level DEBUG
        #    DEBUG Level指出细粒度信息事件对调试应用程序是非常有帮助的。 
        #    static Level INFO
        #    INFO level表明 消息在粗粒度级别上突出强调应用程序的运行过程。 
        #    static Level WARN
        #    WARN level表明会出现潜在错误的情形。 
        #    static Level ERROR
        #    ERROR level指出虽然发生错误事件，但仍然不影响系统的继续运行。 
        #    static Level FATAL
        #    FATAL level指出每个严重的错误事件将会导致应用程序的退出。  
        #    static Level ALL
        #    ALL Level是最低等级的，用于打开所有日志记录。 
        #    static Level OFF
        #    OFF Level是最高等级的，用于关闭所有日志记录。
        #系统的错误（未知)
        self.fail_system = web.storage(code=500, desc='系统处理:内部访问错误, 服务器不能处理该请求！', level='error', error=None) 
        #内部逻辑的错误(已知)
        self.fail_logic = web.storage(code=550, desc='业务处理:逻辑调用出错, 服务器不能处理该请求！', level='info', error=self.fail)   
        #外部接口的错误（未知)
        self.fail_interface = web.storage(code=551, desc='业务处理:调用服务：{%s}出错, 服务器不能处理该请求！', level='error', error=None)   
        #数据库的错误(已知)
        self.fail_db = web.storage(code=552, desc='业务处理:数据调用出错, 服务器不能处理该请求！', level='error', error=None)   
        #数据库的错误(已知)
        self.fail_access = web.storage(code=553, desc='您没有权限进行{%s}的操作！', level='info', error=None)   
         
        if not self.fail_type:
            #默认当前错误是内部逻辑错误
            self.fail_type = self.fail_logic
         
    def __repr__(self):
        response = web.storage()
        response.Code = 200 if self.success else self.fail_type.code
        response.Msg = self.msg if self.msg else ''
        response.DebugMsg = self.fail if not self.success else ''
        response.Data = self.data if self.data else ''
    
        return obj_to_json(response)