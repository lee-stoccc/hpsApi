# coding: utf-8

import web
from core.modules.module_handle import api_handle
from libs.orm.ormutils import dbtranscoped
from models.hps.h_hotel import Hotel
from models.hps.g_guest_doc import GuestDoc
from models.hps.g_guest_checkin import GuestCheckIn
from utils import obj_to_json
from utils.func_api import FuncResult
from utils.tools import is_null, to_datetime, obj_to_json, json_to_obj
import sys, os, uuid, base64, datetime, json, time


class errorLog(object):
    def errorLogging(self, api, param):
        # times = datetime.date.today().strftime('%Y-%m-%d-%H-%M-%S')
        # time2 = time.strftime('%x %X', time.time())
        times = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        dirPathAndTime = self.mkdir()
        textPaht = dirPathAndTime['dirPath'] + '/' + dirPathAndTime['time'] + '.txt'
        if os.path.exists(textPaht):
            f = open(textPaht, 'a')
            f.write("\n" + times + '-' + api + ":" + param + '\n')
            f.write(
                '------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')

            f.close()
        else:
            f = open(textPaht, 'w')
            f.write(times + '-' + api + ":" + param + '\n')
            f.write(
                '------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            f.close()

    def mkdir(self):
        time = str(datetime.date.today().strftime('%y%m%d'))
        dirPath = sys.path[0] + '/errorLog/' + time
        isExist = os.path.exists(dirPath)
        if not isExist:
            os.makedirs(dirPath)
            data = {'dirPath': dirPath, "time": time}
            return data
        else:
            data = {'dirPath': dirPath, "time": time}
            return data
