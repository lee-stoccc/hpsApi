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
import sys, os, uuid, base64, datetime, json
from core.log.getParamLog import Log
import cgi
from core.log.errorLog import errorLog
cgi.maxlen = 10*1024*1024
class handler(object):
    @api_handle(db=True)
    def POST(self):

        # Params = web.input('CerType')
        # image = web.input(image={})
        return self.data_handle()

    @dbtranscoped()
    def data_handle(self):
        try:
            Param = web.input().get('Param')
            if Param == None:
                return FuncResult(fail='Have no Param!')
            logging = Log().logging('UploadHeadPhoto', Param)
            jsonParam = json.loads(Param)
            print "---------------------------------------------------------------------------"
            print " get PMS params :"
            print jsonParam
            print "---------------------------------------------------------------------------"
            Params = jsonParam

            # DocPhotoUrl
            if Params['CerType'] == '1':
                # basePath = Params['basePath'].encode(encoding='UTF-8')
                CerNo = Params['CerNo']
                imageName = Params['ImageName']
                objGuestDoc = GuestDoc().query.filter(GuestDoc.DocNo == CerNo).first()
                newFilePath = mkdir(1) + '/' + str(uuid.uuid1()) + imageName
                newBasePath = base64.b64encode(newFilePath)
                # if have this GuestDoc before:
                if objGuestDoc:
                    CerBaseURL = objGuestDoc.DocPhotoURL
                    if CerBaseURL != None:
                        filePath = base64.b64decode(CerBaseURL)
                        os.remove(filePath)  # delete before photo
                        objGuestDoc.DocPhotoURL = newBasePath
                        objGuestDoc.save()
                fout = open(newFilePath, 'w')
                Img = Params['Img'].replace(' ', '+')
                print '---------------------------------------------------------------------'
                print 'decode begin'
                try:
                    image = base64.b64decode(Img)
                    fout.write(image)
                except Exception,ce:
                    print '-------------------------------------------------------------------'
                    errorLog().errorLogging('UploadHeadPhoto', 'base64 decode fail')
                    print 'decode fail'
                    print '-------------------------------------------------------------------'
                print 'decode end '
                print '--------------------------------------------------------------------'
                resDict = {'DocPhotoURL': newBasePath, 'code': 200}
            # HotelGuestPhotoUrl
            else:
                CerNo = Params['CerNo']
                objGuestCheckIn = GuestCheckIn().query.filter(GuestCheckIn.HotelDocNo == CerNo).first()
                newFilePath = mkdir(0) + '/' + str(uuid.uuid1())
                newBasePath = base64.b64encode(newFilePath)
                if objGuestCheckIn:
                    CerBaseURL = objGuestCheckIn.HotelPhotoURL
                    if CerBaseURL != None:
                        filePath = base64.b64decode(CerBaseURL)
                        os.remove(filePath)  # delete before photo
                        objGuestCheckIn.HotelPhotoURL = newBasePath
                        objGuestCheckIn.save()
                fout = open(newFilePath, 'w')
                Img = Params['Img'].replace(' ', '+')
                image = base64.b64decode(Img)
                fout.write(image)
                resDict = {'DocPhotoURL': newBasePath, 'code': 200}
            return FuncResult(success=True, data=resDict)
        except Exception, ce:
            return FuncResult(fail='upload error ! upload fail!')


def mkdir(type):
    time = datetime.date.today().strftime('%y%m')
    if type == 1:
        dirPath = sys.path[0] + '/DocPhoto/' + str(time)
    else:
        dirPath = sys.path[0] + '/HotelPhoto/' + str(time)
    isExist = os.path.exists(dirPath)
    if not isExist:
        os.makedirs(dirPath)
        return dirPath
    else:
        return dirPath

        # newFilePath = mkdir() + '/' + str(uuid.uuid1()) + image.image.filename
        # newBasePath = base64.b64encode(newFilePath)
        # fout = open(newFilePath, 'w')
        # fout.write(Params['image'])
