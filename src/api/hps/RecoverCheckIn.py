# coding: utf-8

import web
import datetime
from core.log.operate_log import get_log
from core.log.getParamLog import Log
from core.modules.module_handle import api_handle
from libs.orm.ormutils import dbtranscoped
from models.hps.g_guest_checkin import GuestCheckIn
from models.hps.h_relation_checkin import RelationCheckIn
import json
from models.hps.h_hotel import Hotel
from sqlalchemy import desc
from utils.func_api import FuncResult
from utils.tools import is_null, dict_to_name, to_datetime, isHasParams
from models.hps.h_checkin import CheckIn
from core.log.errorLog import errorLog

class handler(object):
    @api_handle(db=True, apiDesc='审核酒店')
    def POST(self):
        return self.data_handle()

    @dbtranscoped()
    def data_handle(self):

        # 获取请求参数
        try:
            Param = web.input().get('Param')
            if Param == None:
                return FuncResult(fail='Have no Param!')
            logging = Log().logging('RecoverCheckIn', Param)
            jsonParam = json.loads(Param)
            print " get PMS params :"
            print "---------------------------------------------------------------------------"
            print jsonParam
            print "---------------------------------------------------------------------------"
            HotelCode = jsonParam['Info']['HotelCode']
            HotelName = jsonParam['Info']['HotelName']
            RoomNo = jsonParam['Info']['RoomNo']
            FolioCode = jsonParam['Info']['FolioCode']
            OperateTime = jsonParam['Info']['OperateTime']
            # Remark = jsonParam['Remark']
        except Exception, ce:
            # 异常处理
            return FuncResult(fail='参数有误!')
        return self.add_hotel(HotelCode, RoomNo, HotelName, FolioCode, OperateTime)

    def add_hotel(self, HotelCode, RoomNo, HotelName, FolioCode, OperateTime):
        try:
            ResOjCheckIn = CheckIn().query2(CheckIn).filter(CheckIn.FolioCode == FolioCode). \
                order_by(desc(CheckIn.CheckInID)).all()
            if ResOjCheckIn:
                objCheckIn = CheckIn()
                resHotel = Hotel().query.filter(Hotel.HotelCode == HotelCode).first()
                if resHotel:
                    objCheckIn.HotelID = resHotel.HotelID
                else:
                    print '--------------------------------------------------------------------'
                    print 'Error !!'
                    print 'Can not find this hotel info!'
                    errorLog().errorLogging('RecoverCheckIn', 'Can not find this hotel info!')
                    print '--------------------------------------------------------------------'
                    return FuncResult(success=False, msg='Can not find this hotel info!')
                objCheckIn.RoomNo = RoomNo
                objCheckIn.RoomTypeCode = ResOjCheckIn[0].RoomTypeCode
                objCheckIn.RoomTypeName = ResOjCheckIn[0].RoomTypeName
                objCheckIn.LastModifyTime = datetime.datetime.now()
                objCheckIn.HotelLastModifyTime = to_datetime(OperateTime)
                objCheckIn.ArrivalTime = ResOjCheckIn[0].ArrivalTime
                objCheckIn.DepartTime = ResOjCheckIn[0].DepartTime
                objCheckIn.CheckInTime = ResOjCheckIn[0].CheckInTime
                objCheckIn.CheckOutTime = ResOjCheckIn[0].CheckOutTime
                objCheckIn.FolioCode = FolioCode
                objCheckIn.FolioState = ResOjCheckIn[0].FolioState
                objCheckIn.CheckInType = 5
                objCheckIn.save(flush=True)

                lsRelaCheckIn = RelationCheckIn().query.filter(
                    RelationCheckIn.CheckInID == ResOjCheckIn[0].CheckInID).all()
                for objRelaCheckIn in lsRelaCheckIn:
                    NewObjRelaCheckIn = RelationCheckIn()
                    NewObjRelaCheckIn.CheckInID = objCheckIn.CheckInID
                    NewObjRelaCheckIn.HotelGuestID = objRelaCheckIn.HotelGuestID
                    NewObjRelaCheckIn.GuestDocID = objRelaCheckIn.GuestDocID
                    NewObjRelaCheckIn.CheckInType = 5
                    NewObjRelaCheckIn.CheckInTime = objRelaCheckIn.CheckInTime
                    NewObjRelaCheckIn.CheckOutTime = objRelaCheckIn.CheckOutTime
                    NewObjRelaCheckIn.GuestState = objRelaCheckIn.GuestState
                    NewObjRelaCheckIn.LastModifyTime = datetime.datetime.now()
                    NewObjRelaCheckIn.HotelLastModifyTime = to_datetime(OperateTime)
                    NewObjRelaCheckIn.save()
                return FuncResult(success=True, msg='Do Success!')
            else:
                print '---------------------------------------------------------------'
                print 'Error !!'
                print 'Can not find this  FolioCode!'
                print '---------------------------------------------------------------'
                errorLog().errorLogging('RecoverCheckIn', 'Can not find this  FolioCode!')
                return FuncResult(success=False, msg='Have No This FolioCode!')
        except Exception, ce:
            return FuncResult(fail=ce)
