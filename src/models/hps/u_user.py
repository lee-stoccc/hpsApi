# coding: utf-8
from libs.orm import OrmBase
from sqlalchemy import Column, Integer, String, DateTime
from libs import web


class User(OrmBase):
    # 表名
    __tablename__ = 'u_user'
    # 表对应的ID
    __tableID__ = 1
    # 类字段

    UserID = Column(Integer, primary_key=True, autoincrement=True, doc='用户ID')
    UserCode = Column(String(100), nullable=True, doc='用户名')
    Password = Column(String(100), nullable=True, doc='密码')
    Tel = Column(String(100), nullable=True, doc='联系方式')
    State = Column(Integer, nullable=True, doc='状态')
    WorkCode = Column(String(100), nullable=True, doc='人员编号')
    UserName = Column(String(100), nullable=True, doc='人员姓名')
    Post = Column(String(100), nullable=True, doc='岗位')
    UserDataRoleList = Column(String(100), nullable=True, doc='数据权限列表')
    RoleList = Column(String(100), nullable=True, doc='功能权限列表')
    Remark = Column(String(100), nullable=True, doc='备注')
    CreateTime = Column(DateTime, nullable=True, doc='创建时间')

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
        self.query = web.ctx.cur_dbsession.query(User)

    def save(self, flush=True):
        '''保存数据(一般的新增和更新都可以在这完成)
        '''
        web.ctx.cur_dbsession.add(self)

        # 如果需要立即执行则更新数据库会话
        if flush:
            web.ctx.cur_dbsession.flush()

    def copy(self, bind=True):
        obj_copy = User(bind)

        obj_copy.UserID = self.UserID
        obj_copy.UserCode = self.UserCode
        obj_copy.Password = self.Password
        obj_copy.Tel = self.Tel
        obj_copy.State = self.State
        obj_copy.WorkCode = self.WorkCode
        obj_copy.UserName = self.UserName
        obj_copy.Post = self.Post
        obj_copy.UserDataRoleList = self.UserDataRoleList
        obj_copy.RoleList = self.RoleList
        obj_copy.Remark = self.Remark
        obj_copy.CreateTime = self.CreateTime

        return obj_copy