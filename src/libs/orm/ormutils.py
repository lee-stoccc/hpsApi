# coding: utf-8
import math

from utils.tools import obj_to_dict
from utils.func_api import FuncResult
from utils.trace_except import get_cur_except
from utils.crypt import des_decrypt
from libs import web
from sqlalchemy import desc
from sqlalchemy.sql.expression import text


def dbtranscoped(config=None):
    '''事务装饰器，用于事务嵌套
        Params:
            @config:参数设置事务控制, 类型是web.storage()
    '''

    def dbtranscopedwrapper(fun):
        def dbtranscopeding(*args, **argkw):
            try:
                # 事务嵌套计数
                web.ctx.cur_trans_count = web.ctx.cur_trans_count + 1
                result = FuncResult()
                if not web.ctx.cur_dbconn.closed:
                    trans = web.ctx.cur_dbconn.begin()
                else:
                    result = FuncResult(fail='数据访问出错， 连接已经关闭')
                    result.fail_type = result.fail_db
                    error = get_cur_except()
                    if error:
                        result.fail_type.error = get_cur_except()[1]
                    return result

                try:
                    result = fun(*args, **argkw)
                    # print result
                    if isinstance(result, FuncResult):
                        # 调用成功提交事务
                        if result.success:
                            if not web.ctx.cur_dbconn.closed:
                                web.ctx.cur_dbsession.flush()
                                web.ctx.cur_dbsession.commit()
                                trans.commit()
                                # 这里在事务提交成功后关闭连接， 防止事务嵌套
                                web.ctx.dbcontext.release_db()
                                # 提交事务计数减1
                                web.ctx.cur_trans_count = web.ctx.cur_trans_count - 1
                    else:
                        raise ValueError, '事务嵌套调用的返回值类型必须是FuncResult对象实例'
                except Exception, ce:
                    rollback = True
                    # 事务回滚
                    if rollback and not web.ctx.cur_dbconn.closed:
                        web.ctx.cur_dbsession.close()
                        trans.rollback()
                        trans.close()
                        # 这里在事务回滚成功后关闭连接， 防止事务嵌套
                        web.ctx.dbcontext.release_db()
                    if not config or not config.raise_error:
                        fail_result = FuncResult()
                        fail_result.fail_type = result.fail_type if isinstance(ce, ValueError) else result.fail_db
                        fail_result.fail_type.error = get_cur_except()[1]
                        fail_result.fail = ce.message if isinstance(ce, ValueError) else str(get_cur_except()[1])
                        return fail_result
            except Exception, ce:
                print get_cur_except()[1]
                fail_result = FuncResult()
                fail_result.fail_type = fail_result.fail_db
                fail_result.fail = str(get_cur_except()[1])
                fail_result.fail_type.error = str(get_cur_except()[1])
                return fail_result
            return result

        return dbtranscopeding

    return dbtranscopedwrapper


def table_query(table_class, query_params, query_params_value, obj_page=None,
                query_columns=None, order='', order_desc='asc', query_all=False):
    '''单个表的数据查询
        Params:
            @table_name:要查询的表名
            @query_params:查询条件参数 例如 FolioCode=:FolioCode
            @query_params_value:查询条件参数值
            @query_columns:查询指定的字段，为空的则查询所有
            @page_size:一页的数据大小, 默认是50
            @page_num:页编码, 默认是1
            @order:排序字段
            @order_desc:排序字段方法, 默认是asc
    '''

    if query_params and not query_params_value: return
    if not query_all:
        if len(query_params) >= 0 and len(query_params_value) <= 0: return

    columns = []
    if query_columns:
        columns = [getattr(table_class, c) for c in query_columns if hasattr(table_class, c)]

    if len(columns) > 0:
        q = web.ctx.cur_dbsession.query(*columns)
    else:
        q = web.ctx.cur_dbsession.query(table_class)

    if query_params:
        match_params = False
        for x in query_params:
            kargs = {}
            for y in query_params_value.keys():
                if x.find(':' + y) >= 0 and query_params_value[y] is not None:
                    kargs[y] = query_params_value[y]
            if len(kargs.keys()) > 0:
                match_params = True
                q = q.filter(x).params(**kargs)

        # 如果参数化的查询没有匹配上对应的值则不可查询
        if not match_params: return

    if order != '':
        if order_desc == 'desc':
            q = q.order_by(desc(order))
        else:
            q = q.order_by(order)

    list_data = []
    total_count = 0
    page_count = 0

    if q:
        # q.options(undefer())
        # 分页需要特殊处理
        if obj_page:
            if obj_page['nPageSize']:
                q = q.limit(obj_page['nPageSize'])
            if obj_page['nPageNo']:
                q = q.offset((obj_page['nPageNo'] - 1) * obj_page['nPageSize'])

            # 分页的时候需要获取记录行数
            sql = q.statement.prefix_with('SQL_CALC_FOUND_ROWS')

            # 查询
            if len(columns) > 0:
                data = web.ctx.cur_dbsession.query(*columns).from_statement(sql).all()
            else:
                data = web.ctx.cur_dbsession.query(table_class).from_statement(sql).all()
        else:
            data = q.all()

        if data:
            for d in data:
                list_data.append(web.storage(**obj_to_dict(d.copy(bind=False))))

            # 分页的时候才需要获取总记录数
            if obj_page:
                rows_count = web.ctx.cur_dbconn.execute(text('SELECT FOUND_ROWS()')).fetchone()

                if rows_count and len(rows_count) > 0:
                    total_count = rows_count[0]
                    page_count = int(math.ceil(total_count / obj_page['nPageSize']))

            return FuncResult(success=True, data={'rowCount': total_count, 'pageCount': page_count, 'data': list_data})

    return FuncResult(success=True, data={'rowCount': total_count, 'pageCount': page_count, 'data': list_data})


def get_data_from_sql(sSql, lsParams, dictParamsValue, objPage=None,
                      sOrder='', sGroup=''):
    '''通过sql查询数据
        Params:
            @sql:指定的sql
            @kargs：对应的参数值
    '''

    if len(lsParams) > 0:
        sSql += ' Where ' + ' And '.join(lsParams)
    if sGroup:
        sSql += ' Group By ' + sGroup
    if sOrder:
        sSql += ' Order By ' + sOrder
    if objPage:
        sSql += ' Limit %s, %s ' % ((objPage['nPageNo'] - 1) * objPage['nPageSize'], objPage['nPageSize'])

    lsQueryData = web.ctx.cur_dbconn.execute(text(sSql), **dictParamsValue).fetchall()
    lsData = []
    nTotalCount = 0
    if lsQueryData:
        if objPage:
            lsRowsCount = web.ctx.cur_dbconn.execute(text('SELECT FOUND_ROWS()')).fetchone()
            if lsRowsCount and len(lsRowsCount) > 0:
                nTotalCount = lsRowsCount[0]

        for d in lsQueryData:
            dictRow = dict(d)
            if dictRow.has_key('GuestName') and dictRow['GuestName']:
                dictRow['GuestName'] = ','.join([des_decrypt(r) for r in dictRow['GuestName'].split(',')])
            if dictRow.has_key('BookPerson'):
                dictRow['BookPerson'] = des_decrypt(dictRow['BookPerson'])
            if dictRow.has_key('ContactPerson'):
                dictRow['ContactPerson'] = des_decrypt(dictRow['ContactPerson'])
            if dictRow.has_key('ContactMobile'):
                dictRow['ContactMobile'] = des_decrypt(dictRow['ContactMobile'])
            if dictRow.has_key('Mobile'):
                dictRow['Mobile'] = des_decrypt(dictRow['Mobile'])

            lsData.append(obj_to_dict(dictRow))

    if objPage:
        return FuncResult(success=True, data={'page_count': nTotalCount, 'data': lsData})
    return FuncResult(success=True, data={'page_count': 0, 'data': lsData})


def get_data(objSql, lsParams, dictParamsValue, objPage=None,
             sOrder='', sGroup='', sOrderDesc='asc'):
    '''通过sql(orm)语句查询
    '''

    if lsParams and not dictParamsValue: return
    if len(lsParams) >= 0 and len(dictParamsValue) <= 0: return

    if lsParams:
        isMatchParams = False
        for sParam in lsParams:
            dictKargs = {}
            for sKey in dictParamsValue.keys():
                if sParam.find(':' + sKey) >= 0 and dictParamsValue[sKey] is not None:
                    dictKargs[sKey] = dictParamsValue[sKey]
            if len(dictKargs.keys()) > 0:
                isMatchParams = True
                objSql = objSql.filter(sParam).params(**dictKargs)

        # 如果参数化的查询没有匹配上对应的值则不可查询
        if not isMatchParams: return

    if sOrder != '':
        if sOrderDesc == 'desc':
            objSql = objSql.order_by(desc(sOrder))
        else:
            objSql = objSql.order_by(sOrder)

    if sGroup != '':
        objSql = objSql.group_by(sGroup)

    lsData = []
    lsDatas = []
    tupDatas = ()
    nTotalCount = 0
    nPageCount = 0

    if objSql:
        # 分页需要特殊处理
        if objPage:
            if objPage['nPageSize']:
                objSql = objSql.limit(objPage['nPageSize'])
            if objPage['nPageNo']:
                objSql = objSql.offset((objPage['nPageNo'] - 1) * objPage['nPageSize'])

            # 分页的时候需要获取记录行数
            objSql2 = objSql.prefix_with('SQL_CALC_FOUND_ROWS')

            # 查询
            tupDatas = objSql2.all()

        if len(tupDatas) > 0:
            for tupData in tupDatas:
                for objData in tupData:
                    lsData.append(obj_to_dict(objData))
                lsDatas.append(lsData)

        # 分页的时候才需要获取总记录数
        if objPage:
            lsRowsCount = web.ctx.cur_dbconn.execute(text('SELECT FOUND_ROWS()')).fetchone()

            if lsRowsCount and len(lsRowsCount) > 0:
                nTotalCount = lsRowsCount[0]
                nPageCount = int(math.ceil(nTotalCount / objPage['nPageSize']))

        return FuncResult(success=True, data={'RowCount': nTotalCount, 'PageCount': nPageCount, 'DataList': lsDatas})

    return FuncResult(success=True, data={'RowCount': nTotalCount, 'PageCount': nPageCount, 'DataList': lsDatas})


# def test(func):
#     def tmp(*args, **kargs):
#         print 'Start %s(%s, %s)...' % (func.__name__, args, kargs)
#         # for sKey in self.__class__.__dict__.keys():
#         #     print sKey
#         #
#         #     if sKey == '__table__':
#         #         objTable = self.__class__.__dict__[sKey]
#         #         objTableCols = objTable._columns.__dict__['_data']
#         #         dictTableCols = dict(objTableCols)
#         #         dictLog = {}
#         #         for sParamsKey in args.keys():
#         #             sLogKey = dictTableCols[sParamsKey].doc
#         #             dictLog[sLogKey] = args[sParamsKey]
#         #         # sLog = obj_to_dict(dictLog)
#         #         print dictLog
#         return func(*args, **kargs)
#     return tmp

