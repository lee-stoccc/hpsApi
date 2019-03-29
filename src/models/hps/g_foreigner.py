# coding: utf-8
from libs.orm import OrmBase
from sqlalchemy import Column, Integer, String, DateTime
from libs import web


class Foreigner(OrmBase):
    # 表名
    __tablename__ = 'g_foreigner'
    # 表对应的ID
    TableID = 10
    # 类字段

    ForeignerID = Column(Integer, primary_key=True, autoincrement=True, doc='旅客档案ID')
    GuestDocID = Column(Integer, nullable=True, doc='旅客证件信息ID')
    PassNo = Column(String(111), nullable=True, doc='护照编号')
    VisaDeadline = Column(DateTime, nullable=True, doc='签证失效时间')
    DepartureTime = Column(DateTime, nullable=True, doc='离境时间')
    EntryTime = Column(DateTime, nullable=True, doc='入境时间')
    EntryPlace = Column(String(100), nullable=True, doc='入境地点')
    DeparturePlace = Column(String(100), nullable=True, doc='离境地点')
    VisaType = Column(String(11), nullable=True, doc='签证类型')
    Nationality = Column(String(11), nullable=True, doc='国籍')
    CreateTime = Column(Integer, nullable=True, doc='创建时间')

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
        self.query = web.ctx.cur_dbsession.query(Foreigner)

    def save(self, flush=True):
        '''保存数据(一般的新增和更新都可以在这完成)
        '''
        web.ctx.cur_dbsession.add(self)

        # 如果需要立即执行则更新数据库会话
        if flush:
            web.ctx.cur_dbsession.flush()

    def copy(self, bind=True):
        obj_copy = Foreigner(bind)

        obj_copy.ForeignerID = self.ForeignerID
        obj_copy.GuestDocID = self.GuestDocID
        obj_copy.PassNo = self.PassNo
        obj_copy.VisaDeadline = self.VisaDeadline
        obj_copy.DepartureTime = self.DepartureTime
        obj_copy.EntryTime = self.EntryTime
        obj_copy.EntryPlace  = self.EntryPlace
        obj_copy.DeparturePlace = self.DeparturePlace
        obj_copy.VisaType = self.VisaType
        obj_copy.Nationality = self.Nationality
        obj_copy.CreateTime = self.CreateTime

        return obj_copy