# coding: utf-8
from libs.orm import OrmBase
from sqlalchemy import Column, Integer, DateTime, String
from libs import web


class District(OrmBase):
    # 表名
    __tablename__ = 's_district'
    # 表对应的ID
    TableID = 14
    # 类字段

    DistrictID = Column(Integer, primary_key=True, autoincrement=True, doc='区/县ID')
    ProvinceID = Column(Integer, nullable=True, doc='省份ID')
    District = Column(String(50), nullable=True, doc='区/县名称')
    CityID = Column(Integer, nullable=True, doc='市/州ID')
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
        self.query = web.ctx.cur_dbsession.query(District)

    def save(self, flush=True):
        '''保存数据(一般的新增和更新都可以在这完成)
        '''
        web.ctx.cur_dbsession.add(self)

        # 如果需要立即执行则更新数据库会话
        if flush:
            web.ctx.cur_dbsession.flush()

    def copy(self, bind=True):
        obj_copy = District(bind)

        obj_copy.DistrictID = self.DistrictID
        obj_copy.ProvinceID = self.ProvinceID
        obj_copy.District = self.District
        obj_copy.CityID = self.CityID
        obj_copy.IsFlag = self.IsFlag

        return obj_copy