# coding: utf-8

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OrmBase(Base):
    __abstract__ = True

    # 生成日志
    def GetLogDescription(self, dictParams=None):
        dictTableCols = {}
        dictLog = {}
        for sKey in self.__class__.__dict__.keys():
            if sKey == '__table__':
                objTable = self.__class__.__dict__[sKey]
                objTableCols = objTable._columns.__dict__['_data']
                dictTableCols = dict(objTableCols)
        if not dictParams:
            dictParams = self.GetParams(dictTableCols)
        for sParamsKey in dictParams.keys():
            sLogKey = dictTableCols[sParamsKey].doc
            dictLog[sLogKey] = dictParams[sParamsKey]
        if dictLog:
            return str(dictLog).decode('string_escape')
        else:
            return ''

    # 获取需要记录到日志的字段及值
    def GetParams(self, dictTableCols):
        dictParams = {}
        for sColKey in dictTableCols.keys():
            if getattr(self, sColKey):
                dictParams[sColKey]= getattr(self, sColKey)
        return dictParams

