# coding: utf-8
'''
Created on 2013-12-23

@author: Administrator
'''
from libs import web
from utils.tools import obj_to_dict, json_to_obj
from utils.func_api import FuncResult

def get_request_page_params():
    '''获取请求参数
    '''
    web.header('Content-Type', 'text/plain')
    try:
        params = web.storage()
        params.userid = web.input().get('userid')
        query_columns = web.input().get('query_columns')
        query_params = web.input().get('query_params')
        query_params_value = web.input().get('query_params_value')
        
        if query_columns:query_columns = json_to_obj(query_columns)
        if query_params:query_params = json_to_obj(query_params)
        if query_params_value:query_params_value = json_to_obj(query_params_value)
    
        params.query_columns = query_columns   
        params.query_params = query_params or []
        params.query_params_value = query_params_value or {}
         
        ispage = web.input().get('ispage') 
        
        if ispage: ispage = ispage.lower().strip() == 'true'
        params.ispage = ispage or False
        
        page_num = web.input().get('page_num')
        if page_num: page_num = int(page_num)
        params.page_num = page_num or 0
        
        page_size = web.input().get('page_size') 
        if page_size: page_size = int(page_size)
        params.page_size = page_size or 0
        
        params.order = web.input().get('order', '')
         
        params.order_desc = web.input().get('order_desc', '') 

        return FuncResult(success=True, value=params) 
    except Exception, ce:   
        print ce.message
        return FuncResult(fail='传入参数json格式有误!') 