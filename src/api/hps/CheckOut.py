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
from models.hps.CheckOutParam import CheckOutParam
from core.log.getParamLog import Log
from core.log.errorLog import errorLog


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
        objCheckOut = CheckOutParam(CheckInFolioParam=jsonParam['CheckInFolio'],
                                        GuestSetParams=jsonParam['GuestSet'], ACT=jsonParam['ACT'])
        return self.add_hotel(CheckInInfo, GuestInfoSet)

    def add_hotel(sHotelCode, HotelCode, CheckOutTime, GuesetCode, FolioCode, OperateTime):
        try:
            ResOjCheckIn = CheckIn().query2(CheckIn).filter(CheckIn.FolioCode == FolioCode). \
                order_by(desc(CheckIn.CheckInID)).all()
            if ResOjCheckIn:
                objCheckIn = CheckIn()
                resHotel = Hotel().query.filter(Hotel.HotelCode == HotelCode).first()
                if resHotel:
                    objCheckIn.HotelID = resHotel.HotelID
                else:
                    print '---------------------------------------------------------------'
                    print 'Error !!'
                    print 'Can not find this hotel info!'
                    print '---------------------------------------------------------------'
                    errorLog().errorLogging('CheckOut', 'Can not find this hotel info!')
                    return FuncResult(success=False, msg='Can not find this hotel info!')
                objCheckIn.RoomNo = ResOjCheckIn[0].RoomNo
                objCheckIn.RoomTypeCode = ResOjCheckIn[0].RoomTypeCode
                objCheckIn.RoomTypeName = ResOjCheckIn[0].RoomTypeName
                objCheckIn.LastModifyTime = datetime.datetime.now()
                objCheckIn.HotelLastModifyTime = to_datetime(OperateTime)
                objCheckIn.ArrivalTime = ResOjCheckIn[0].ArrivalTime
                objCheckIn.DepartTime = to_datetime(CheckOutTime)
                objCheckIn.CheckInTime = ResOjCheckIn[0].CheckInTime
                objCheckIn.CheckOutTime = to_datetime(CheckOutTime)
                objCheckIn.FolioCode = FolioCode
                objCheckIn.FolioState = ResOjCheckIn[0].FolioState
                objCheckIn.CheckInType = 4
                objCheckIn.save(flush=True)

                lsRelaCheckIn = RelationCheckIn().query.filter(
                    RelationCheckIn.CheckInID == ResOjCheckIn[0].CheckInID).all()
                for objRelaCheckIn in lsRelaCheckIn:
                    NewObjRelaCheckIn = RelationCheckIn()
                    NewObjRelaCheckIn.CheckInID = objCheckIn.CheckInID
                    NewObjRelaCheckIn.HotelGuestID = objRelaCheckIn.HotelGuestID
                    NewObjRelaCheckIn.GuestDocID = objRelaCheckIn.GuestDocID
                    NewObjRelaCheckIn.CheckInType = 4
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
                errorLog().errorLogging('CheckOut', 'Can not find this  FolioCode!')
                return FuncResult(success=False, msg='Have No This FolioCode!')
        except Exception, ce:
            return FuncResult(fail=ce)
