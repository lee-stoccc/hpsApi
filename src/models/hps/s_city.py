# coding: utf-8
from libs.orm import OrmBase
from sqlalchemy import Column, Integer, DateTime, String
from libs import web


class City(OrmBase):
    # 表名
    __tablename__ = 's_city'
    # 表对应的ID
    TableID = 13
    # 类字段

    CityID = Column(Integer, primary_key=True, autoincrement=True, doc='城市ID')
    CityName = Column(String(50), nullable=True, doc='城市名称')
    ProvinceID = Column(Integer, nullable=True, doc='省份ID')
    IsCapitalCity = Column(Integer, nullable=True, doc='是否为省会城市')
    IsFlag = Column(Integer, nullable=True, doc='是否有效')

    def __init__(self, bind=True):
        '''数据类初始化
        '''
        if bind:
            self.bind_db()

    def bind_db(self):
        '''跟数据库绑定
        '''
        # 初始化数据类的结构
        self.metadata.bind = web.cache.db[web.ctx.dbcontext.conn_str].engine
        # 初始化数据类查询
        self.query = web.ctx.cur_dbsession.query(City)

    def save(self, flush=True):
        '''保存数据(一般的新增和更新都可以在这完成)
        '''
        web.ctx.cur_dbsession.add(self)

        # 如果需要立即执行则更新数据库会话
        if flush:
            web.ctx.cur_dbsession.flush()

    def copy(self, bind=True):
        obj_copy = City(bind)

        obj_copy.CityID = self.CityID
        obj_copy.CityName = self.CityName
        obj_copy.ProvinceID = self.ProvinceID
        obj_copy.IsCapitalCity = self.IsCapitalCity
        obj_copy.IsFlag = self.IsFlag

        return obj_copy