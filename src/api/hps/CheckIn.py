# coding: utf-8

import web
import datetime
from core.log.operate_log import get_log
from core.modules.module_handle import api_handle
from libs.orm.ormutils import dbtranscoped
from models.hps.h_hotel import Hotel
from models.hps.g_guest_checkin import GuestCheckIn
from models.hps.h_relation_checkin import RelationCheckIn
from models.hps.g_foreigner import Foreigner
from models.hps.g_guest_doc import GuestDoc
import json
from utils.func_api import FuncResult
from utils.tools import is_null, dict_to_name, to_datetime, isHasParams, timestampTodatatime
import sys, os
from models.hps.h_checkin import CheckIn
from core.log.getParamLog import Log
import cgi
from models.hps.CheckOutParam import CheckOutParam
import time
import uuid, base64
from sqlalchemy import desc

cgi.maxlen = 10 * 1024 * 1024


class handler(object):
    @api_handle(db=True, apiDesc='审核酒店')
    def POST(self):
        return self.data_handle()

    @dbtranscoped()
    def data_handle(self):
        try:
            Param = web.input().get('Param')
            if Param == None:
                return FuncResult(fail='Have no Param!')
            Log().logging('CheckIn', Param)
            jsonParam = json.loads(Param)
        except Exception, ce:
            return FuncResult(fail='Param format error!')
        CheckInParams = CheckOutParam(CheckInFolioParam=jsonParam['CheckInFolio'],
                                      GuestSetParams=jsonParam['GuestSet'], ACT=jsonParam['ACT'])
        return self.CheckIn(CheckInParams)

    def CheckIn(self, CheckInParams):
        try:
            # save CheckInTable
            objCheckIn = CheckIn()
            # find HotelID with HotelCode
            resHotel = Hotel().query.filter(Hotel.HotelCode == CheckInParams.CheckInFolio['HotelCode']).first()
            if resHotel:
                objCheckIn.HotelID = resHotel.HotelID
            else:
                return FuncResult(success=False, msg='Can not find this hotel info!')
            objCheckIn.FolioCode = CheckInParams.CheckInFolio['FolioCode']
            objCheckIn.CheckInTime = timestampTodatatime(CheckInParams.CheckInFolio['CheckInTime'])
            objCheckIn.CheckOutTime = timestampTodatatime(CheckInParams.CheckInFolio['CheckOutTime'])
            objCheckIn.RoomNo = CheckInParams.CheckInFolio['RoomNo']
            objCheckIn.HotelLastModifyTime = timestampTodatatime(CheckInParams.CheckInFolio['PMSOperateTime'])
            objCheckIn.LastModifyTime = datetime.datetime.now()
            objCheckIn.CheckInType = CheckInParams.ACT
            objCheckIn.save(flush=True)
            newCheckInID = objCheckIn.CheckInID

            # save GuesetInfo
            for GuestParam in CheckInParams.GuestSet:
                objGuestTable = GuestCheckIn()
                objDocTable = GuestDoc()
                IDCardImage = GuestParam['IDAuthenticationResult']['IDCardImage']  # IDCardImage base64
                MatchImage = GuestParam['IDAuthenticationResult']['MatchImage']  # MatchImage base64
                # save GuestTable
                objGuestTable.HotelDocType = GuestParam['Guest']['HotelDocType']
                objGuestTable.HotelDocNo = GuestParam['Guest']['HotelDocNo']
                objGuestTable.HotelDocName = GuestParam['Guest']['HotelDocName']
                objGuestTable.HotelGuestName = GuestParam['Guest']['HotelGuestName']
                objGuestTable.HotelBornDate = timestampTodatatime(GuestParam['Guest']['HotelBornDate'])
                objGuestTable.HotelSex = GuestParam['Guest']['HotelSex']
                objGuestTable.HotelNationality = GuestParam['Guest']['NationaCode']  # guoji
                objGuestTable.HotelNation = GuestParam['Guest']['HotelNation']  # minzu
                objGuestTable.HotelAddress = GuestParam['Guest']['HotelAddress']
                objGuestTable.HotelRemark = GuestParam['Guest']['HotelRemark']
                objGuestTable.HotelTel = GuestParam['Guest']['HotelTel']
                objGuestTable.HotelLastModifyTime = timestampTodatatime(CheckInParams.CheckInFolio['PMSOperateTime'])
                objGuestTable.LastModifyTime = datetime.datetime.now()
                objGuestTable.MatchResult = GuestParam['IDAuthenticationResult']['MatchResult']
                objGuestTable.MatchResultPercent = GuestParam['IDAuthenticationResult']['MatchResultPercent']
                # if ACT != 1  not checkin ?
                if not CheckInParams.ACT == 1:
                    guestBeforeInfo = GuestCheckIn().query.filter(
                        GuestCheckIn.HotelDocNo == GuestParam['Guest']['HotelDocNo']).filter(
                        GuestCheckIn.HotelPhotoURL.isnot(None)).order_by(
                        desc(GuestCheckIn.HotelGuestID)).all()
                    if not guestBeforeInfo == []:
                        objGuestTable.HotelPhotoURL = guestBeforeInfo[0].HotelPhotoURL
                else:
                    imageBase64 = GuestParam['IDAuthenticationResult']['MatchImage']
                    objGuestTable.HotelPhotoURL = self.saveHeadImage(imageType=2, imageBase64=imageBase64)
                    pass  # ACT =1 checkin
                objGuestTable.save(flush=True)
                newGuestID = objGuestTable.HotelGuestID

                # if is foreigner and save foreignerTable
                if GuestParam['Guest']['IsForeigner'] == 1:
                    foreignerTable = Foreigner()
                    foreignerTable.GuestDocID = newGuestID
                    foreignerTable.PassNo = GuestParam['Guest']['PassNo']
                    foreignerTable.VisaDeadline = timestampTodatatime(GuestParam['Guest']['VisaDeadline'])
                    foreignerTable.DepartureTime = timestampTodatatime(GuestParam['Guest']['DepartureTime'])
                    foreignerTable.EntryTime = timestampTodatatime(GuestParam['Guest']['EntryTime'])
                    foreignerTable.EntryPlace = GuestParam['Guest']['EntryPlace']
                    foreignerTable.DeparturePlace = GuestParam['Guest']['DeparturePlace']
                    foreignerTable.VisaType = GuestParam['Guest']['VisaType']
                    foreignerTable.CreateTime = datetime.datetime.now()
                    foreignerTable.Nationality = GuestParam['Guest']['NationaCode']
                    foreignerTable.save(flush=True)
                    newForeignerID = foreignerTable.ForeignerID

                # save DocTable
                objDocTable.GuestType = GuestParam['Doc']['GuestType']
                objDocTable.DocType = GuestParam['Doc']['DocType']
                objDocTable.DocNo = GuestParam['Doc']['DocNo']
                objDocTable.DocName = GuestParam['Doc']['DocName']
                objDocTable.GuestName = GuestParam['Doc']['GuestName']
                objDocTable.BornDate = timestampTodatatime(GuestParam['Doc']['BornDate'])
                objDocTable.Sex = GuestParam['Doc']['Sex']
                objDocTable.NativePlace = GuestParam['Doc']['NativePlace']
                objDocTable.Nation = GuestParam['Doc']['Nation']
                objDocTable.AuthStatus = GuestParam['Doc']['AuthStatus']
                objDocTable.ResAddress = GuestParam['Doc']['ResAddress']
                objDocTable.State = GuestParam['Doc']['State']
                objDocTable.CertiOffice = GuestParam['Doc']['CertiOffice']
                objDocTable.CertiEffStartTime = timestampTodatatime(GuestParam['Doc']['CertiEffStartTime'])
                objDocTable.CertiEffEndTime = timestampTodatatime(GuestParam['Doc']['CertiEffEndTime'])
                objDocTable.Remark = GuestParam['Doc']['Remark']
                objDocTable.CreateTime = datetime.datetime.now()
                if not CheckInParams.ACT == 1:
                    docBeforeInfo = GuestDoc().query.filter(
                        GuestDoc.DocNo == GuestParam['Doc']['DocNo']).filter(
                        GuestDoc.DocPhotoURL.isnot(None)).order_by(desc(GuestDoc.GuestDocID)).all()
                    if not docBeforeInfo == []:
                        objDocTable.DocPhotoURL = docBeforeInfo[0].DocPhotoURL
                else:
                    imageBase64 = GuestParam['IDAuthenticationResult']['IDCardImage']
                    objDocTable.DocPhotoURL = self.saveHeadImage(imageType=1, imageBase64=imageBase64)
                objDocTable.save(flush=True)
                newDocID = objDocTable.GuestDocID

                # save in h_relation_checkin  table
                self.addRealtionCheckIn(newCheckInID, newGuestID, newDocID, CheckInParams)
            return FuncResult(success=True, msg='操作成功!')
        except Exception, ce:
            return FuncResult(fail=ce)

    def addRealtionCheckIn(self, newCheckInID, newGuestID, newDocID, CheckInParams):
        objRelationCheckIn = RelationCheckIn()
        objRelationCheckIn.CheckInID = newCheckInID
        objRelationCheckIn.HotelGuestID = newGuestID
        objRelationCheckIn.GuestDocID = newDocID
        objRelationCheckIn.CheckInType = CheckInParams.ACT
        objRelationCheckIn.CheckInTime = timestampTodatatime(CheckInParams.CheckInFolio['CheckInTime'])
        objRelationCheckIn.CheckOutTime = timestampTodatatime(CheckInParams.CheckInFolio['CheckOutTime'])
        objRelationCheckIn.LastModifyTime = datetime.datetime.now()
        objRelationCheckIn.HotelLastModifyTime = timestampTodatatime(CheckInParams.CheckInFolio['PMSOperateTime'])
        objRelationCheckIn.save()
        pass

    def saveHeadImage(self, imageType, imageBase64):
        # save IDCardImage
        if imageType == 1:
            FilePath = self.mkdir(1) + '/' + str(uuid.uuid1()) + 'a.jpeg'

        else:
            # save Gueset
            FilePath = self.mkdir(2) + '/' + str(uuid.uuid1()) + 'a.jpeg'
        BasePath = base64.b64encode(FilePath)
        try:
            imageBase64 = imageBase64.replace(' ', '+')
            fileParam = base64.b64decode(imageBase64)
            File = open(FilePath, 'w')
            File.write(fileParam)
            File.close()
        except Exception, ce:
            return
        return BasePath

    # 1:doc  2:guest
    def mkdir(self, type):
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
