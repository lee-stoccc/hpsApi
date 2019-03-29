# coding: utf-8

import pprint
import socket
import os
import re
import json
import decimal
import uuid
from datetime import date, datetime
from libs import web
from sqlalchemy.util import NoneType
import string
import random as numrandom
from dateutil import parser
import xlwt
import StringIO
from models.hps.l_dictionary import Dictionary
import time

NONCE_CHARS = string.letters + string.digits
TIME_FMT = '%Y-%m-%dT%H:%M:%SZ'


def dict_to_name(nDictNum, dDict):
    '''
    字典对象转换 数字-》中文名
        nDictNum: 需转换的字段值
        dDict: 字典对象
    '''
    if web.cache.has_key(dDict):
        if nDictNum:
            sDictName = web.cache[dDict][nDictNum]
        else:
            sDictName = ''

        return sDictName
    return ''


def get_dict():
    '''缓存字典表数据'''
    lsDicType = Dictionary().query.group_by(Dictionary.TypeName).all()

    for objDictType in lsDicType:
        lsDict = []
        lsDictionary = web.ctx.cur_dbsession. \
            query(Dictionary.CodeName, Dictionary.CodeNo). \
            filter(Dictionary.TypeName == objDictType.TypeName). \
            all()
        for objDict in lsDictionary:
            tupDict = (objDict.CodeNo, objDict.CodeName)
            lsDict.append(tupDict)

        dictDinctionary = dict(lsDict)
        web.cache[objDictType.TypeName] = dictDinctionary


def str_to_bigcamel(str_param, str_separator):
    str_list = str(str_param).split(str_separator)[1:]
    camel_list = [item.capitalize() for item in str_list]
    return ''.join(camel_list)


def is_null(x):
    if isinstance(x, str):
        # print 1
        if x.strip() == '':
            return True
        return False
    elif isinstance(x, dict) and x != None:
        # print 2
        if not any(x):
            return True
        return False
    elif isinstance(x, list):
        # print 3
        if not x:
            return True
        return False
    # print 4
    return not x


def prettify(x):
    '''print格式化
        Params:
            @x:需要打印出来的信息
    '''
    try:
        out = pprint.pformat(x)
    except Exception, e:
        out = str(e)
    return out


if os.name != "nt":
    #    import fcntl
    import struct


    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return ''


def get_server_ip():
    '''获取服务器的ip地址
    '''
    return ['127.0.0.1']
    return [socket.gethostname(), get_local_ip(), get_lan_ip()]


def get_lan_ip():
    '''获取服务器的内部ip地址 
    '''
    return ['127.0.0.1']
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
        ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip


def get_local_ip():
    '''获取服务器的本地ip地址 
    '''
    return '127.0.0.1'
    ip_list = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:-1]
    if len(ip_list) > 0:
        return ip_list[0]
    return '127.0.0.1'


def obj_to_json(obj):
    '''将对象转成json
    '''
    try:
        return json.dumps(obj, default=json_default, ensure_ascii=False, encoding='utf-8')
    except Exception, ce:
        print ce.message
        try:
            return json.dumps(obj, default=json_default, ensure_ascii=True, encoding='gbk')
        except:
            return json.dumps(obj, default=json_default)


def json_parser(json_obj):
    for p in json_obj.keys():
        value = json_obj[p]
        if type(value) == str or type(value) == unicode:
            try:
                if p not in ['Remarks', 'Remark', 'InnerRemarks', 'ForegiftCodes', 'InvoiceCodes', 'Address']:
                    if len(value) == 10:
                        json_obj[p] = datetime.strptime(value, '%Y-%m-%d')
                    else:
                        json_obj[p] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except:
                pass

    return json_obj


def json_to_obj(json_dict):
    '''将字符json转换成对象
        Params:
            @json_dict:字符json
    '''
    if type(json_dict) not in [str, unicode]:
        return json_dict

    json_dict = json_dict.replace('\r', '\\r')
    json_dict = json_dict.replace('\n', '\\n')
    json_dict = json_dict.replace('\t', '')  # 去tab
    return json.loads(json_dict, object_hook=json_parser)


def json_default(obj):
    '''json字符的默认处理
        Params:
            @obj:json字符对象
    '''
    if isinstance(obj, NoneType):
        return ''
    if isinstance(obj, datetime):
        if obj.year < 1900:
            return str(obj)
        else:
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(obj, date):
        if obj.year < 1900:
            return str(obj)
        else:
            return obj.strftime('%Y-%m-%d')
    else:
        raise TypeError('%r is not JSON serializable' % obj)


def obj_to_dict(obj):
    '''将对象转成字典
        Params:
            @obj:需要转换的对象
    '''

    record = {}
    if type(obj) == dict or isinstance(obj, web.Storage):
        for p in obj.keys():
            value = obj[p]
            if type(value) == NoneType:
                record[p] = ''
                continue
            if type(value) == datetime or type(value) == date:
                try:
                    record[p] = datetime.strftime(value, '%Y-%m-%d %H:%M:%S')
                except:
                    record[p] = value
            elif isinstance(value, decimal.Decimal):
                record[p] = float(value)
            elif type(value) == unicode:
                record[p] = value
                if os.name == 'nt':
                    try:
                        record[p] = ''.join(chr(ord(x)) for x in value).decode('gbk')
                    except:
                        record[p] = value
            else:
                record[p] = value
    else:
        obj_info = dir(obj)
        for p in obj_info:
            if p[0] == "_" or p in ['metadata']: continue
            value = getattr(obj, p)
            if callable(value): continue

            if type(value) == NoneType:
                record[p] = ''
                continue
            if type(value) == datetime or type(value) == date:
                try:
                    record[p] = datetime.strftime(value, '%Y-%m-%d %H:%M:%S')
                except:
                    record[p] = str(value)
            elif isinstance(value, decimal.Decimal):
                record[p] = float(value)
            elif type(value) == unicode:
                record[p] = value
                if os.name == 'nt':
                    try:
                        record[p] = ''.join(chr(ord(x)) for x in value).decode('gbk')
                    except:
                        record[p] = value
            else:
                record[p] = value

    return record


def gen_nonce(len=6):
    '''生产随机数， 默认长度是6位
    '''
    return ''.join(numrandom.sample(NONCE_CHARS, len))


def get_fs_sequence(seq_dir, seq_date):
    '''通过文件系统获取序列号
    '''
    retry = 10
    while retry > 0:
        retry = retry - 1
        try:
            # 如果目录不存在则返回0, 表示失败
            if not os.path.exists(seq_dir):
                return 0

            files = os.listdir(dir)
            if files:
                seq_file = files[0]
                seq_info = seq_file.split('-')
                last_date = parser.parse(seq_info[0])
                cur_date_str = datetime.strftime(seq_date, '%Y%m%d')
                cur_date = parser.parse(cur_date_str)
                # 锁定更新操作
                # 首先先强制更新该文件， 如果更新成功则表示已经可以给当前进程锁住
                temp_new_seq_file = seq_info[0] + '-' + seq_info[1] + '-' + str(uuid.uuid4().get_time())
                os.rename(seq_file, temp_new_seq_file)
                # 当前序列号
                curid = int(seq_info[1])
                # 如果上一个记录的日期居然大于当前指定日期
                # 表明服务器的时间出现问题
                if last_date > cur_date:
                    return 0  # 表示失败
                if last_date == cur_date:
                    # 当前序列号加一
                    nextid = curid + 1
                else:
                    # 日期增长后重置序列号
                    nextid = 1

                new_seq_file = cur_date_str + '-' + str(nextid) + '-' + str(uuid.uuid4().get_time())
                # 更新文件， 如果更新失败证明序列号已经发生变化，则重试
                os.rename(temp_new_seq_file, new_seq_file)
                # 更新成功则返回新的序列号
                return nextid
            else:
                filename = datetime.strftime(seq_date, '%Y%m%d') + '-1'
                with open(filename, 'w') as f:
                    f.write('')
                return 1  # 初始值是1
        except Exception, ce:
            pass

    return 0


from dateutil.relativedelta import relativedelta
from dateutil.parser import parse


def get_month_range(date):
    """ 获取当前日期的当月的第一天和最后一天
    """
    first_day = date + relativedelta(day=1)
    last_day = date + relativedelta(day=1, months=+1, days=-1)
    return first_day, last_day


def get_week_range(date):
    """ 获取当前日期的当周的第一天和最后一天
    """
    first_day = date + relativedelta(weekday=0, weeks=-1, days=-1)
    last_day = date + relativedelta(weekday=-1)
    return first_day, last_day


def get_date_inrange(d, range):
    '''获取指定日期是否在某个时间段内
    '''
    return d >= parse(range[0] + ' 00:00:00') and d <= parse(range[1] + ' 23:59:59')


def export_excel(title, lst_headers, dic_data):
    '''导出Excel
    '''
    web.header('Content-type', 'application/vnd.ms-excel')  # 指定返回的类型
    web.header('Transfer-Encoding', 'chunked')
    web.header('Content-Disposition', 'attachment;filename="' + title + '.xls"')  # 设定用户浏览器显示的保存文件名
    wb = xlwt.Workbook()
    wb.encoding = 'gbk'
    ws = wb.add_sheet(title)
    row = 1
    col = 0
    for k in lst_headers:
        ws.write(0, col, k[1])  # 如果要写中文请使用UNICODE
        col = col + 1

    for r in dic_data:
        col = 0
        for k in lst_headers:
            try:
                if type(r[k[0]]) not in (str, unicode, float):
                    print r[k[0]]
                    r[k[0]] = r[k[0]].strftime('%Y-%m-%d %H:%M:%S')  # 如果时间格式不对则转换后写入
                    ws.write(row, col, r[k[0]])  # 如果要写中文请使用UNICODE
                else:
                    ws.write(row, col, r[k[0]])
            except:
                ws.write(row, col, '/')
            col = col + 1
        row = row + 1

    sio = StringIO.StringIO()
    wb.save(sio)  # 这点很重要，传给save函数的不是保存文件名，而是一个StringIO流

    web.ctx.direct_response = True
    return sio.getvalue()


def check_idcard(idcardno):
    area = {"11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古", "21": "辽宁", "22": "吉林", "23": "黑龙江",
            "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东", "41": "河南", "42": "湖北",
            "43": "湖南", "44": "广东", "45": "广西", "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南", "54": "西藏",
            "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆", "71": "台湾", "81": "香港", "82": "澳门", "91": "国外"}
    idcard = str(idcardno)
    idcard = idcard.strip()
    idcard_list = list(idcard)
    try:
        # 地区校验
        if (not area[(idcard)[0:2]]):
            return False
        # 15位身份号码检测
        if (len(idcard) == 15):
            if ((int(idcard[6:8]) + 1900) % 4 == 0 or (
                                (int(idcard[6:8]) + 1900) % 100 == 0 and (int(idcard[6:8]) + 1900) % 4 == 0)):
                erg = re.compile(
                    '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')  # //测试出生日期的合法性
            else:
                ereg = re.compile(
                    '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')  # //测试出生日期的合法性
            if (re.match(ereg, idcard)):
                return True
            else:
                return False
        # 18位身份号码检测
        elif (len(idcard) == 18):
            # 出生日期的合法性检查
            # 闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
            # 平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
            if (int(idcard[6:10]) % 4 == 0 or (int(idcard[6:10]) % 100 == 0 and int(idcard[6:10]) % 4 == 0)):
                ereg = re.compile(
                    '[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')  # //闰年出生日期的合法性正则表达式
            else:
                ereg = re.compile(
                    '[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')  # //平年出生日期的合法性正则表达式
            # //测试出生日期的合法性
            if (re.match(ereg, idcard)):
                # //计算校验位
                S = (int(idcard_list[0]) + int(idcard_list[10])) * 7 + (int(idcard_list[1]) + int(
                    idcard_list[11])) * 9 + (int(idcard_list[2]) + int(idcard_list[12])) * 10 + (int(
                    idcard_list[3]) + int(idcard_list[13])) * 5 + \
                    (int(idcard_list[4]) + int(idcard_list[14])) * 8 + (int(idcard_list[5]) + int(
                    idcard_list[15])) * 4 + (int(idcard_list[6]) + int(idcard_list[16])) * 2 + int(
                    idcard_list[7]) * 1 + int(idcard_list[8]) * 6 + int(idcard_list[9]) * 3
                Y = S % 11
                M = "F"
                JYM = "10X98765432"
                M = JYM[Y]  # 判断校验位
                if (M == idcard_list[17]):  # 检测ID的校验位
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    except:
        return False

    return True


def get_doc_area(idcardno):
    area = {"11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古", "21": "辽宁", "22": "吉林", "23": "黑龙江",
            "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东", "41": "河南", "42": "湖北",
            "43": "湖南", "44": "广东", "45": "广西", "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南", "54": "西藏",
            "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆", "71": "台湾", "81": "香港", "82": "澳门", "91": "国外"}
    if area.get(idcardno[0:2]):
        return area[idcardno[0:2]]


def get_birth(idcardno):
    if len(idcardno) == 15:
        return parse(str(int(idcardno[6:8]) + 1900) + idcardno[8:12]).date()
    elif len(idcardno) == 18:
        return parse(idcardno[6:14]).date()


def str2camel(param):
    if type(param) == 'str':
        list = list(param)


def to_datetime(value):
    '''转换为日期类型
    '''
    try:
        if type(value) != unicode:
            strVlaue = date.strftime(value, "%Y-%m-%d %H:%M:%S")
        else:
            strVlaue = value
        if len(strVlaue) == 10:
            return datetime.strptime(strVlaue, "%Y-%m-%d")
        else:
            # if len(value) > 20:
            return datetime.strptime(strVlaue, "%Y-%m-%d %H:%M:%S")
    except Exception, ce:
        print ce
        return False


def get_params(classname):
    return


def days_count(sStartDay, sEndDay):
    dtStartDay = datetime.strptime(sStartDay, '%Y-%m-%d')
    dtEndDay = datetime.strptime(sEndDay, '%Y-%m-%d')
    if dtEndDay < dtStartDay:
        return "error"
    ndays = (dtEndDay - dtStartDay).days + 1
    return ndays


def result_data(PageNO, PageSize, RowCount, DateSet):
    Data = {}
    Data['PageNO'] = PageNO
    Data['PageSize'] = PageSize
    Data['RowCount'] = RowCount
    Data['DataSet'] = DateSet
    return Data


def isHasParams(key, dict):
    if key in dict and dict[key] and dict[key] != '':
        return True
    else:
        return False


def timestampTodatatime(timestamp):
    t = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", t)
