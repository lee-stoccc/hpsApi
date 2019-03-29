# coding: utf-8
from libs.orm import OrmBase
from sqlalchemy import Column, Integer, String, DateTime
from libs import web


class Certificates(OrmBase):
    # 表名
    __tablename__ = 'h_certificates'
    # 表对应的ID
    TableID = 20
    # 类字段

    ID = Column(Integer, primary_key=True, autoincrement=True, doc='ID')
    UID = Column(Integer, nullable=True, doc='')
    HotelID = Column(Integer, nullable=True, doc='')
    CertificatesType = Column(Integer, nullable=True, doc='')
    CertificatesURL = Column(Integer, nullable=True, doc='')
    IsFront = Column(Integer, nullable=True, doc='')
    IsFlag = Column(Integer, nullable=True, doc='')
    CreateTime = Column(DateTime, nullable=True, doc='')

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
        self.query = web.ctx.cur_dbsession.query(Certificates)

    def save(self, flush=True):
        '''保存数据(一般的新增和更新都可以在这完成)
        '''
        web.ctx.cur_dbsession.add(self)

        # 如果需要立即执行则更新数据库会话
        if flush:
            web.ctx.cur_dbsession.flush()

    def copy(self, bind=True):
        obj_copy = Certificates(bind)
        obj_copy.ID = self.ID
        obj_copy.UID = self.UID
        obj_copy.HotelID = self.HotelID
        obj_copy.CertificatesType = self.CertificatesType
        obj_copy.CertificatesURL = self.CertificatesURL
        obj_copy.IsFront = self.IsFront
        obj_copy.IsFlag  = self.IsFlag
        obj_copy.CreateTime = self.CreateTime
        return obj_copy