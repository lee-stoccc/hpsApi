# coding: utf-8

import web
import datetime
from core.log.operate_log import get_log
from core.modules.module_handle import api_handle
from libs.orm.ormutils import dbtranscoped
from models.hps.g_guest_checkin import GuestCheckIn
from models.hps.g_guest_doc import GuestDoc
from models.hps.h_hotel import Hotel
from models.hps.h_relation_checkin import RelationCheckIn
import json
from sqlalchemy import desc
from utils.func_api import FuncResult
from utils.tools import is_null, dict_to_name, to_datetime, isHasParams

from models.hps.h_checkin import CheckIn
from core.log.getParamLog import Log
from core.log.errorLog import errorLog
import cgi

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
            logging = Log().logging('ReduceGuests', Param)
            jsonParam = json.loads(Param)
            print "---------------------------------------------------------------------------"
            print " get PMS params :"
            print jsonParam
            print "---------------------------------------------------------------------------"
            lsReduce = jsonParam['Reduce']
            for objReduce in lsReduce:
                GuestCode = objReduce['CheckOut']['GuestCode']
                HotelCode = objReduce['CheckOut']['HotelCode']
                CheckOutTime = objReduce['CheckOut']['CheckOutTime']
                FolioCode = objReduce['CheckOut']['FolioCode']
                OperateTime = objReduce['CheckOut']['OperateTime']
                Res = self.add_hotel(GuestCode, HotelCode, CheckOutTime, FolioCode, OperateTime)
            if Res == 1:
                print '---------------------------------------------------------------'
                print 'Error !!'
                print 'Can not find this folio!'
                print '---------------------------------------------------------------'
                errorLog().errorLogging('ReduceGuests', 'Can not find this  folio!')
                return FuncResult(success=False, msg='Can not find this folio')
            elif Res == 2:
                print '---------------------------------------------------------------'
                print 'Error !!'
                print 'Can not find this hotel info!'
                print '---------------------------------------------------------------'
                errorLog().errorLogging('ReduceGuests', 'Can not find this hotel info!')
                return FuncResult(success=False, msg='Can not find this hotel info')
            elif Res == 3:
                print '---------------------------------------------------------------'
                print 'Error !!'
                print 'Can not find this hotel guest!'
                print '---------------------------------------------------------------'
                errorLog().errorLogging('ReduceGuests', 'Can not find this guest!')
                return FuncResult(success=False, msg='Can not find this guest')
            elif Res == 4:
                errorLog().errorLogging('ReduceGuests', 'Logic error , can not find this checkIn folio!')
                return FuncResult(success=False, msg='Logic error , can not find this checkIn folio!')
            else:
                return FuncResult(success=True, msg='Do Success!')
                # return FuncResult(success=True, msg='Do Success!')
        except Exception, ce:
            # 异常处理
            return FuncResult(fail='参数有误!')

    def add_hotel(self, GuestCode, HotelCode, CheckOutTime, FolioCode, OperateTime):
        try:
            ResOjCheckIn = CheckIn().query2(CheckIn).filter(CheckIn.FolioCode == FolioCode). \
                order_by(desc(CheckIn.CheckInID)).all()
            if ResOjCheckIn:
                objCheckIn = CheckIn()
                resHotel = Hotel().query.filter(Hotel.HotelCode == HotelCode).first()
                if resHotel:
                    objCheckIn.HotelID = resHotel.HotelID
                else:
                    # return FuncResult(success=False, msg='Can not find this hotel info!')
                    return 2
                objCheckIn.RoomNo = ResOjCheckIn[0].RoomNo
                objCheckIn.RoomTypeCode = ResOjCheckIn[0].RoomTypeCode
                objCheckIn.RoomTypeName = ResOjCheckIn[0].RoomTypeName
                objCheckIn.LastModifyTime = datetime.datetime.now()
                objCheckIn.HotelLastModifyTime = to_datetime(OperateTime)
                objCheckIn.ArrivalTime = ResOjCheckIn[0].ArrivalTime
                objCheckIn.DepartTime = ResOjCheckIn[0].DepartTime
                objCheckIn.CheckInTime = ResOjCheckIn[0].CheckInTime
                objCheckIn.CheckOutTime = to_datetime(CheckOutTime)
                objCheckIn.FolioCode = FolioCode
                objCheckIn.FolioState = ResOjCheckIn[0].FolioState
                objCheckIn.CheckInType = 7
                objCheckIn.save(flush=True)

                # find which ReduceGuest
                # resDocInfo = GuestDoc().query.filter(GuestDoc.DocNo == DocNo).first()

                resGuestInfo = GuestCheckIn().query.filter(GuestCheckIn.HotelDocNo == GuestCode).first()
                RelaInfo = RelationCheckIn().query.filter(
                    RelationCheckIn.HotelGuestID == resGuestInfo.HotelGuestID).all()

                if RelaInfo == None or resGuestInfo == None:
                    # return FuncResult(success=False, msg='Have No This Guest!')
                    return 3
                # save in new relation_checkin table
                lsRelaCheckIn = RelationCheckIn().query.filter(
                    RelationCheckIn.CheckInID == ResOjCheckIn[0].CheckInID).all()
                if lsRelaCheckIn ==None or lsRelaCheckIn == []:
                    return 4
                for objRelaCheckIn in lsRelaCheckIn:
                    NewObjRelaCheckIn = RelationCheckIn()
                    NewObjRelaCheckIn.CheckInID = objCheckIn.CheckInID
                    NewObjRelaCheckIn.HotelGuestID = resGuestInfo.HotelGuestID
                    NewObjRelaCheckIn.GuestDocID = RelaInfo[0].GuestDocID
                    NewObjRelaCheckIn.CheckInType = 7
                    NewObjRelaCheckIn.CheckInTime = objRelaCheckIn.CheckInTime
                    NewObjRelaCheckIn.CheckOutTime = to_datetime(CheckOutTime)
                    NewObjRelaCheckIn.GuestState = objRelaCheckIn.GuestState
                    NewObjRelaCheckIn.LastModifyTime = datetime.datetime.now()
                    NewObjRelaCheckIn.HotelLastModifyTime = to_datetime(OperateTime)
                    NewObjRelaCheckIn.save()
                    # return FuncResult(success=True, msg='Do Success!')
                    # return 0
            else:
                return 1
        except Exception, ce:
            return FuncResult(fail=ce)
