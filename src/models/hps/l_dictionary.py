# coding: utf-8
from libs.orm import OrmBase
from sqlalchemy import Column, Integer, DateTime, String
from libs import web


class Dictionary(OrmBase):
    # 表名
    __tablename__ = 'l_dictionary'
    # 表对应的ID
    TableID = 17
    # 类字段

    CodeID = Column(Integer, primary_key=True, autoincrement=True, doc='字典ID')
    CodeType = Column(Integer, nullable=True, doc='字典数据类型编号')
    TypeName = Column(String(100), nullable=True, doc='字典数据类型名称')
    CodeNo = Column(Integer, nullable=True, doc='数据编号')
    CodeName = Column(String(20), nullable=True, doc='数据名称')
    Sort = Column(Integer, nullable=True, doc='排序')
    ExtendInfo = Column(String(100), nullable=True)
    Flag = Column(Integer, nullable=True, doc='是否有效')
    CodeEnumName= Column(String(100), nullable=True)

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
        self.query = web.ctx.cur_dbsession.query(Dictionary)

    def save(self, flush=True):
        '''保存数据(一般的新增和更新都可以在这完成)
        '''
        web.ctx.cur_dbsession.add(self)

        # 如果需要立即执行则更新数据库会话
        if flush:
            web.ctx.cur_dbsession.flush()

    def copy(self, bind=True):
        obj_copy = Dictionary(bind)

        obj_copy.CodeID = self.CodeID
        obj_copy.CodeType = self.CodeType
        obj_copy.TypeName = self.TypeName
        obj_copy.CodeNo = self.CodeNo
        obj_copy.CodeName = self.CodeName
        obj_copy.Sort = self.Sort
        obj_copy.ExtendInfo  = self.ExtendInfo
        obj_copy.Flag = self.Flag
        obj_copy.CodeEnumName= self.CodeEnumName

        return obj_copy