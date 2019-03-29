﻿# coding: utf-8

import os 
from libs import web
from sqlalchemy import util
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

from utils import get_dict


class LazyDBConn():
    '''延迟打开数据库连接
    '''
    def __init__(self, dbcontext=None):
        self.dbcontext = dbcontext 
        
    def __getattr__(self, key): 
        if self.dbcontext and not self.dbcontext.conn: 
            try:
                self.dbcontext.conn = web.cache.db[self.dbcontext.conn_str].engine.connect()
  
                self.dbcontext.conn.execute('Select 1')
                
                    
            except exc.DBAPIError, e:
                if e.connection_invalidated:
                    print '断线重连...........' + e.message
                    #断线重连
                    self.dbcontext.conn = web.cache.db[self.dbcontext.conn_str].engine.connect()
            except Exception, e:
                self.dbcontext.conn = web.cache.db[self.dbcontext.conn_str].engine.connect()
                    
        data = getattr(self.dbcontext.conn, key)
        return data

          
    def __repr__(self):     
        if self.dbcontext and self.dbcontext.conn:
            return repr(self.dbcontext.conn)
        
    
    
class LazyDBSession(): 
    '''延迟打开数据库连接会话
    '''
    def __init__(self, dbcontext=None):
        self.dbcontext = dbcontext
       
        
    def __getattr__(self, key): 
        if self.dbcontext and not self.dbcontext.session: 
            
            Session = sessionmaker(autocommit=False, autoflush=True, bind=web.cache.db[self.dbcontext.conn_str].engine)
            
            if self.dbcontext and not self.dbcontext.conn:
                
                try:
                    self.dbcontext.conn = web.cache.db[self.dbcontext.conn_str].engine.connect()
                    self.dbcontext.conn.execute('Select 1')
                except exc.DBAPIError, e:
                    if e.connection_invalidated:
                        print '断线重连...........' + e.message
                        #断线重连
                        self.dbcontext.conn = web.cache.db[self.dbcontext.conn_str].engine.connect()
                except Exception, e:
                    self.dbcontext.conn = web.cache.db[self.dbcontext.conn_str].engine.connect()
                           
            self.dbcontext.session = Session(bind=self.dbcontext.conn)
          
        data = getattr(self.dbcontext.session, key)
        return data
          
    def __repr__(self):   
        if self.dbcontext and self.dbcontext.session:
            return repr(self.dbcontext.session)

class DBContext():
    '''数据库操作对象上下文
    '''
    def __init__(self, conn_str=None):
        
        self.conn_str = conn_str
        self.conn = None
        self.session = None
        self.init_db()
         
        
    def init_db(self):
        '''初始化数据库
        '''    
        if not web.cache.db.has_key(self.conn_str): 
            if os.name == "nt": 
                db_engine = create_engine(self.conn_str, connect_args={'charset':'utf8',}, echo=False, 
                                               pool_recycle=5, pool_size=10, max_overflow=5)
                
                
            else: 
                db_engine = create_engine(self.conn_str, 
                                               connect_args={'charset':'utf8',}, 
                                               echo=False, convert_unicode=True,
                                               pool_recycle=10, pool_size=50, max_overflow=20)

            
            db_metadata = MetaData(db_engine)  
            #缓存当前连接的基本信息
            web.cache.db[self.conn_str] = web.storage()
            web.cache.db[self.conn_str].engine = db_engine 
            web.cache.db[self.conn_str].metadata = db_metadata 
            web.cache.db[self.conn_str].tables = {} 
            web.cache.db[self.conn_str].tables_class = {}

 
    @property
    def dbconn(self): 
        '''当前数据库连接
        '''
        return LazyDBConn(self)
    
    @property
    def dbsession(self):
        '''当前数据库连接会话
        '''
        return LazyDBSession(self)  
            

    def release_db(self):
        '''释放数据库
        '''
        try: 
            if self.session:
                self.session.close()
            if self.conn and not self.conn.closed: 
                self.conn.close()  
        except:
            pass 