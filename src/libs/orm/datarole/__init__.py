#coding UTF-8
from libs.orm import OrmBase

class DataRoue(object):
    def Filter(self, objOrmBase, data_list):
        return data_list

    def GenrateSqlFilter(self, objOrmBase):
        return None

    def __LoadTableDataRule(self, sTableName, nUserID):
        pass