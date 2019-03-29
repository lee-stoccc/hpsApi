class CheckOutParam(object):
    def __init__(self, CheckInFolioParam, GuestSetParams, ACT=1):
        self.ACT = ACT
        errorParams = []
        self.CheckInFolio = {}
        self.GuestSet = []
        self.CheckInFolioVerify = ['HotelCode', 'FolioCode', 'CheckInTime', 'CheckOutTime',
                                   'RoomNo', 'Remark', 'PMSOperateTime']

        self.GuestVerify = ['HotelDocType', 'HotelDocNo', 'HotelDocName','HotelGuestName', 'HotelBornDate', 'HotelSex', 'NationaCode',
                            'HotelNation', 'HotelAddress', 'HotelRemark', 'HotelTel', 'IsForeigner', 'GuestDocID',
                            'PassNo', 'VisaDeadline', 'DepartureTime', 'EntryTime', 'EntryPlace', 'DeparturePlace',
                            'VisaType', 'HotelPhotoURL']
        self.DocVerify = [
            "GuestType", "DocType", "DocNo", "DocName", "GuestName", "BornDate", "Sex", "NativePlace", "Nation",
            "AuthStatus", "ResAddress", "State", "CertiOffice", "CertiEffStartTime", "CertiEffEndTime", "DocPhotoURL",
            "Remark"]

        self.IDResultVerify = ["DocNo", "DocType", "DocName", "MatchResultPercent", "MatchResult", "IDCardImage", "MatchImage"]

        # Verify CheckInFolio Col
        for i in range(len(self.CheckInFolioVerify)):
            if self.isHasParams(self.CheckInFolioVerify[i], CheckInFolioParam):
                # self.__dict__[CheckInFolioKey] = CheckInFolioParam[CheckInFolioKey]
                self.CheckInFolio[self.CheckInFolioVerify[i]] = CheckInFolioParam[self.CheckInFolioVerify[i]]
            else:
                errorParams.append(self.CheckInFolioVerify[i])
                self.errorParams = errorParams

        objGuest = {}
        objDoc = {}
        objIDResult = {}
        for j in range(len(GuestSetParams)):
            # Verify Guest Col
            for k in range(len(self.GuestVerify)):
                if self.isHasParams(self.GuestVerify[k], GuestSetParams[j]['Guest']):
                    objGuest[self.GuestVerify[k]] = GuestSetParams[j]['Guest'][self.GuestVerify[k]]
                else:
                    errorParams.append(self.GuestVerify[k] + ':' + str(j))
                    self.errorParams = errorParams

            # Verify Doc Col
            for k in range(len(self.DocVerify)):
                if self.isHasParams(self.DocVerify[k], GuestSetParams[j]['Doc']):
                    objDoc[self.DocVerify[k]] = GuestSetParams[j]['Doc'][self.DocVerify[k]]
                else:
                    errorParams.append(self.DocVerify[k] + ':' + str(j))
                    self.errorParams = errorParams

            # Verify IDAuthenticationResult Col
            for k in range(len(self.IDResultVerify)):
                if self.isHasParams(self.IDResultVerify[k], GuestSetParams[j]['IDAuthenticationResult']):
                    objIDResult[self.IDResultVerify[k]] = GuestSetParams[j]['IDAuthenticationResult'][
                        self.IDResultVerify[k]]
                else:
                    errorParams.append(self.IDResultVerify[k] + ':' + str(j))
                    self.errorParams = errorParams
            self.GuestSet.append({'Guest': objGuest, 'Doc': objDoc, 'IDAuthenticationResult': objIDResult})
            objGuest = {}
            objDoc = {}
            objIDResult = {}

        del self.CheckInFolioVerify
        del self.GuestVerify
        del self.IDResultVerify
        del self.DocVerify

    def isHasParams(self, key, dict):
        if key in dict:
            return True
        else:
            return False


            # self.CheckInFolioVerify = {
            #     'HotelCode': 'HotelCode',
            #     'FolioCode': 'FolioCode',
            #     'CheckInTime': 'CheckInTime',
            #     'CheckOutTime': 'CheckOutTime',
            #     'RoomNo': 'RoomNo',
            #     'Remark': 'Remark',
            #     'PMSOperateTime': 'PMSOperateTime'
            # }
