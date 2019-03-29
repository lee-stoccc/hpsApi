# coding: utf-8

import web
import datetime
from core.log.operate_log import get_log
from core.modules.module_handle import api_handle
from libs.orm.ormutils import dbtranscoped
from models.hps.g_guest_checkin import GuestCheckIn
from models.hps.h_relation_checkin import RelationCheckIn
from models.hps.h_hotel import Hotel
import json
from sqlalchemy import desc
from utils.func_api import FuncResult
from utils.tools import is_null, dict_to_name, to_datetime, isHasParams

from models.hps.h_checkin import CheckIn
from core.log.getParamLog import Log
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
            logging = Log().logging('ContinueStaying', Param)
            jsonParam = json.loads(Param)
            print " get PMS params :"
            print "---------------------------------------------------------------------------"
            print jsonParam
            print "---------------------------------------------------------------------------"
            HotelCode = jsonParam['ContinueStaying']['HotelCode']
            HotelName = jsonParam['ContinueStaying']['HotelName']
            RoomNo = jsonParam['ContinueStaying']['RoomNo']
            FolioCode = jsonParam['ContinueStaying']['FolioCode']
            NewCheckOutTime = jsonParam['ContinueStaying']['NewCheckOutTime']
            OperateTime = jsonParam['ContinueStaying']['OperateTime']
            # Remark = jsonParam['ContinueStaying']['Remark']

        except Exception, ce:
            # 异常处理
            return FuncResult(fail='参数有误!')
        return self.add_hotel(HotelCode, RoomNo, HotelName, NewCheckOutTime,
                              FolioCode, OperateTime)

    def add_hotel(self, HotelCode, RoomNo, HotelName, NewCheckOutTime,
                  FolioCode, OperateTime):
        try:
            ResOjCheckIn = CheckIn().query2(CheckIn).filter(CheckIn.FolioCode == FolioCode). \
                order_by(desc(CheckIn.CheckInID)).all()
            if ResOjCheckIn:
                objCheckIn = CheckIn()
                resHotel = Hotel().query.filter(Hotel.HotelCode ==HotelCode).first()
                if resHotel:
                    objCheckIn.HotelID = resHotel.HotelID
                else:
                    print '---------------------------------------------------------------'
                    print 'Error !!'
                    print 'Can not find this hotel info!'
                    print '---------------------------------------------------------------'
                    errorLog().errorLogging('ContinueStayingAPI', 'Can not find this hotel info!')
                    return FuncResult(success=False, msg='Can not find this hotel info!')
                objCheckIn.RoomNo = RoomNo
                objCheckIn.RoomTypeCode = ResOjCheckIn[0].RoomTypeCode
                objCheckIn.RoomTypeName = ResOjCheckIn[0].RoomTypeName
                objCheckIn.LastModifyTime = datetime.datetime.now()
                objCheckIn.HotelLastModifyTime = to_datetime(OperateTime)
                objCheckIn.ArrivalTime = ResOjCheckIn[0].ArrivalTime
                objCheckIn.DepartTime = ResOjCheckIn[0].DepartTime

                objCheckIn.CheckInTime = ResOjCheckIn[0].CheckInTime
                objCheckIn.CheckOutTime = to_datetime(NewCheckOutTime)
                objCheckIn.FolioCode = FolioCode
                objCheckIn.FolioState = ResOjCheckIn[0].FolioState
                objCheckIn.CheckInType = 3
                objCheckIn.save(flush=True)

                lsRelaCheckIn = RelationCheckIn().query.filter(
                    RelationCheckIn.CheckInID == ResOjCheckIn[0].CheckInID).all()
                for objRelaCheckIn in lsRelaCheckIn:
                    NewObjRelaCheckIn = RelationCheckIn()
                    NewObjRelaCheckIn.CheckInID = objCheckIn.CheckInID
                    NewObjRelaCheckIn.HotelGuestID = objRelaCheckIn.HotelGuestID
                    NewObjRelaCheckIn.GuestDocID = objRelaCheckIn.GuestDocID
                    NewObjRelaCheckIn.CheckInType = 3
                    NewObjRelaCheckIn.CheckInTime = objRelaCheckIn.CheckInTime
                    NewObjRelaCheckIn.CheckOutTime = NewCheckOutTime
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
                errorLog().errorLogging('ContinueStayingAPI', 'Can not find this  FolioCode!')
                return FuncResult(success=False, msg='Have No This FolioCode!')
        except Exception, ce:
            return FuncResult(fail=ce)
