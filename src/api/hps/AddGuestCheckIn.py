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
from sqlalchemy import desc
from utils.func_api import FuncResult
from utils.tools import is_null, dict_to_name, to_datetime, isHasParams

from models.hps.h_checkin import CheckIn
from core.log.getParamLog import Log
from core.log.errorLog import errorLog
import cgi
cgi.maxlen = 10*1024*1024
class handler(object):
    @api_handle(db=True, apiDesc='审核酒店')
    def POST(self):
        return self.data_handle()

    @dbtranscoped()
    def data_handle(self):
        # 获取请求参数
        objInput = web.input()
        try:
            Param = web.input().get('Param')
            if Param == None:
                return FuncResult(fail='Have no Param!')
            Log().logging('AddGuestCheckIn', Param)
            jsonParam = json.loads(Param)
            print "---------------------------------------------------------------------------"
            print " get PMS params :"
            print jsonParam
            print "---------------------------------------------------------------------------"
            CheckInInfo = jsonParam['CheckInInfo']
            GuestInfoSet = jsonParam['GuestInfoSet']
            if is_null(CheckInInfo):
                return FuncResult(fail='参数：CheckInInfo不能为空')
            if is_null(GuestInfoSet):
                return FuncResult(fail='参数：GuestInfoSet不能为空')
        except Exception, ce:
            # 异常处理
            return FuncResult(fail='参数有误!')
        return self.add_hotel(CheckInInfo, GuestInfoSet)

    def add_hotel(self, CheckInInfo, GuestInfoSet):
        try:
            # save CheckIn
            objCheckIn = CheckIn()
            # oldCheckIn = CheckIn().query.filter(CheckIn.FolioCode == CheckInInfo['FolioCode']).\
            #     order_by(desc(CheckIn.CheckInID)).all()
            if isHasParams('HotelCode', CheckInInfo):
                resHotel = Hotel().query.filter(Hotel.HotelCode == CheckInInfo['HotelCode']).first()
                if resHotel:
                    objCheckIn.HotelID = resHotel.HotelID
                else:
                    print '--------------------------------------------------------------------'
                    print 'Error !!'
                    print 'Can not find this hotel info!'
                    errorLog().errorLogging('AddGuestCheckInAPI', 'Can not find this hotel info!')
                    print '--------------------------------------------------------------------'
                    return FuncResult(success=False, msg='Can not find this hotel info!')
            else:
                print '--------------------------------------------------------------------'
                print 'Error !!'
                print 'Can not find this hotel info!'
                print '--------------------------------------------------------------------'
                errorLog().errorLogging('AddGuestCheckInAPI', 'Can not find this hotel info!')
                return FuncResult(success=False, msg='Can not find this hotel info!')
            if isHasParams('RoomNo', CheckInInfo):
                objCheckIn.RoomNo = CheckInInfo['RoomNo']
            if isHasParams('RoomTypeCode', CheckInInfo):
                objCheckIn.RoomTypeCode = CheckInInfo['RoomTypeCode']
            if isHasParams('RoomTypeName', CheckInInfo):
                objCheckIn.RoomTypeName = CheckInInfo['RoomTypeName']
            if isHasParams('ArrivalTime', CheckInInfo):
                objCheckIn.ArrivalTime = to_datetime(CheckInInfo['ArrivalTime'])
                objCheckIn.CheckInTime = to_datetime(CheckInInfo['ArrivalTime'])
            if isHasParams('DepartTime', CheckInInfo):
                objCheckIn.DepartTime = to_datetime(CheckInInfo['DepartTime'])
                objCheckIn.CheckOutTime = to_datetime(CheckInInfo['DepartTime'])
            if isHasParams('FolioCode', CheckInInfo):
                objCheckIn.FolioCode = CheckInInfo['FolioCode']
            objCheckIn.LastModifyTime = datetime.datetime.now()
            objCheckIn.CheckInType = 6
            objCheckIn.save(flush=True)
            CheckInID = objCheckIn.CheckInID

            # save GuesetInfo
            for GuestInfo in GuestInfoSet:
                objGuestInfo = GuestCheckIn()
                objDocInfo = GuestDoc()
                dictGuestInfo = GuestInfo['GuestInfo']
                dictDocInfo = GuestInfo['DocInfo']
                # have this GuesetInfo before ?
                resGuestInfo = GuestCheckIn().query.filter(
                    GuestCheckIn.HotelDocNo == dictGuestInfo['HotelDocNo']).first()
                if not resGuestInfo:
                    if isHasParams('HotelDocType', dictGuestInfo):
                        objGuestInfo.HotelDocType = dictGuestInfo['HotelDocType']
                    if isHasParams('HotelDocNo', dictGuestInfo):
                        objGuestInfo.HotelDocNo = dictGuestInfo['HotelDocNo']
                    if isHasParams('HotelDocName', dictGuestInfo):
                        objGuestInfo.HotelDocName = dictGuestInfo['HotelDocName']
                    if isHasParams('HotelBornDate', dictGuestInfo):
                        objGuestInfo.HotelBornDate = dictGuestInfo['HotelBornDate']
                    if isHasParams('HotelSex', dictGuestInfo):
                        objGuestInfo.HotelSex = dictGuestInfo['HotelSex']
                    if isHasParams('NationaCode', dictGuestInfo):
                        objGuestInfo.HotelNation = dictGuestInfo['NationaCode']
                    if isHasParams('HotelAddress', dictGuestInfo):
                        objGuestInfo.HotelAddress = dictGuestInfo['HotelAddress']
                    if isHasParams('HotelRemark', dictGuestInfo):
                        objGuestInfo.HotelRemark = dictGuestInfo['HotelRemark']
                    if isHasParams('HotelLastModifyTime', dictGuestInfo):
                        objGuestInfo.HotelLastModifyTime = to_datetime(dictGuestInfo['HotelLastModifyTime'])
                    if isHasParams('HotelTel', dictGuestInfo):
                        objGuestInfo.HotelTel = dictGuestInfo['HotelTel']
                    if isHasParams('MatchResult', dictDocInfo):
                        objGuestInfo.MatchResult = dictDocInfo['MatchResult']
                    if isHasParams('MatchResultPercent', dictDocInfo):
                        objGuestInfo.MatchResultPercent = dictDocInfo['MatchResultPercent']
                    objGuestInfo.save(flush=True)
                    HotelGuestID = objGuestInfo.HotelGuestID
                else:
                    HotelGuestID = resGuestInfo.HotelGuestID

                # have this GuestDocID before ?
                resGuestDocInfo = GuestDoc().query.filter(GuestDoc.DocNo == dictDocInfo['DocNo']).first()
                if not resGuestDocInfo:
                    if isHasParams('GuestType', dictDocInfo):
                        objDocInfo.GuestType = dictDocInfo['GuestType']
                    if isHasParams('GuestType', dictDocInfo):
                        objDocInfo.GuestType = dictDocInfo['GuestType']
                    if isHasParams('DocType', dictDocInfo):
                        objDocInfo.DocType = dictDocInfo['DocType']
                    if isHasParams('DocNo', dictDocInfo):
                        objDocInfo.DocNo = dictDocInfo['DocNo']
                    if isHasParams('DocName', dictDocInfo):
                        objDocInfo.DocName = dictDocInfo['DocName']
                    if isHasParams('GuestName', dictDocInfo):
                        objDocInfo.GuestName = dictDocInfo['GuestName']
                    if isHasParams('BornDate', dictDocInfo):
                        objDocInfo.BornDate = dictDocInfo['BornDate']
                    if isHasParams('Sex', dictDocInfo):
                        objDocInfo.Sex = dictDocInfo['Sex']
                    if isHasParams('NativePlace', dictDocInfo):
                        objDocInfo.NativePlace = dictDocInfo['NativePlace']
                    if isHasParams('Nation', dictDocInfo):
                        objDocInfo.Nation = dictDocInfo['Nation']
                    if isHasParams('AuthStatus', dictDocInfo):
                        objDocInfo.AuthStatus = dictDocInfo['AuthStatus']
                    if isHasParams('ResAddress', dictDocInfo):
                        objDocInfo.ResAddress = dictDocInfo['ResAddress']
                    if isHasParams('State', dictDocInfo):
                        objDocInfo.State = dictDocInfo['State']
                    if isHasParams('CertiOffice', dictDocInfo):
                        objDocInfo.CertiOffice = dictDocInfo['CertiOffice']
                    if isHasParams('CertiEffStartTime', dictDocInfo):
                        objDocInfo.CertiEffStartTime = to_datetime(dictDocInfo['CertiEffStartTime'])
                    if isHasParams('CertiEffEndTime', dictDocInfo):
                        objDocInfo.CertiEffEndTime = to_datetime(dictDocInfo['CertiEffEndTime'])
                    if isHasParams('DocPhotoURL', dictDocInfo):
                        objDocInfo.DocPhotoURL = dictDocInfo['DocPhotoURL']
                    if isHasParams('Remark', dictDocInfo):
                        objDocInfo.Remark = dictDocInfo['Remark']
                    objDocInfo.CreateTime = datetime.datetime.now()
                    objDocInfo.save(flush=True)
                    GuestDocID = objDocInfo.GuestDocID
                else:
                    GuestDocID = resGuestDocInfo.GuestDocID

                if isHasParams('IsForeigner', dictGuestInfo):
                    # if is foreigner
                    if dictGuestInfo['IsForeigner']:
                        objForeigner = Foreigner()
                        # have this foreigner before ?
                        resForeigner = Foreigner().query.filter(Foreigner.PassNo == dictGuestInfo['PassNo']).first()
                        if not resForeigner:
                            if isHasParams('GuestDocID', dictGuestInfo):
                                objForeigner.GuestDocID = GuestDocID
                            if isHasParams('PassNo', dictGuestInfo):
                                objForeigner.PassNo = dictGuestInfo['PassNo']
                            if isHasParams('VisaDeadline', dictGuestInfo):
                                objForeigner.VisaDeadline = dictGuestInfo['VisaDeadline']
                            if isHasParams('DepartureTime', dictGuestInfo):
                                objForeigner.DepartureTime = dictGuestInfo['DepartureTime']
                            if isHasParams('EntryTime', dictGuestInfo):
                                objForeigner.EntryTime = dictGuestInfo['EntryTime']
                            if isHasParams('EntryPlace', dictGuestInfo):
                                objForeigner.EntryPlace = dictGuestInfo['EntryPlace']
                            if isHasParams('DeparturePlace', dictGuestInfo):
                                objForeigner.DeparturePlace = dictGuestInfo['DeparturePlace']
                            if isHasParams('VisaType', dictGuestInfo):
                                objForeigner.VisaType = dictGuestInfo['VisaType']
                            objForeigner.CreateTime = datetime.datetime.now()
                            objForeigner.save(flush=True)
                # save in h_relation_checkin  table
                self.addRealtionCheckIn(CheckInID, HotelGuestID, GuestDocID, CheckInInfo)
                print 22
            return FuncResult(success=True, msg='操作成功!')
        except Exception, ce:
            return FuncResult(fail=ce)

    def addRealtionCheckIn(self, CheckInID, HotelGuestID, GuestDocID, CheckInInfo):
        objRelationCheckIn = RelationCheckIn()
        objRelationCheckIn.CheckInID = CheckInID
        objRelationCheckIn.HotelGuestID = HotelGuestID
        objRelationCheckIn.GuestDocID = GuestDocID
        objRelationCheckIn.CheckInType = 6
        objRelationCheckIn.CheckInTime = to_datetime(CheckInInfo['ArrivalTime'])
        objRelationCheckIn.CheckOutTime = to_datetime(CheckInInfo['DepartTime'])
        objRelationCheckIn.LastModifyTime = datetime.datetime.now()
        objRelationCheckIn.HotelLastModifyTime = to_datetime(CheckInInfo['OperateTime'])
        objRelationCheckIn.save()
        pass
