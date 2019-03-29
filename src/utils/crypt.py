# coding: utf-8


import binascii
import random

from Crypto.Cipher import AES
from pyDes import des, CBC, PAD_PKCS5

from libs import web
import hashlib
from rsa import PrivateKey, PublicKey, sign, verify, encrypt, decrypt

def aes_encrypt(data=None):
    '''aes加密数据
    '''
    if not data:
        return
    key = 'hps'
    sIv = md5_encrypt('hps','')[0:16]
    length = 16
    aes_key = length - (len(key) % length)
    key = key + ('\0' * aes_key)
    cryptor = AES.new(key, AES.MODE_CBC, sIv)
    # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用

    add_data = length - (len(data) % length)
    data = data + ('\0' * add_data)

    ciphertext = cryptor.encrypt(data)
    # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
    # 所以这里统一把加密后的字符串转化为16进制字符串
    return binascii.b2a_hex(ciphertext)


def aes_decrypt(data=None):
    '''aes解密数据
    '''
    if not data:
        return
    key = 'hps'
    sIv = md5_encrypt('hps','')[0:16]
    length = 16
    aes_key = length - (len(key) % length)
    key = key + ('\0' * aes_key)
    cryptor = AES.new(key, AES.MODE_CBC, sIv)
    plain_text = cryptor.decrypt(binascii.a2b_hex(data))
    # 解密后，去掉补足的空格用strip() 去掉
    return plain_text.rstrip('\0')

  
def des_encrypt(data=None, key=None):
    '''des加密数据
    '''
    if not data: return data
    try:
        if not key:
            key = 'hps'
            if web.ctx.session.get('user'):
                key = web.ctx.session.user['UserCode'] + 'hps'

        k = des(str(key[0:8]), CBC, str(key[0:8]), pad=None, padmode=PAD_PKCS5)

        res = binascii.b2a_hex(k.encrypt(str(data).encode('GBK')))
        
        return res
    except Exception,ce:
        print ce.message
        return data
    
def des_decrypt(data=None, key=None):
    '''解密数据
    '''
    if not data: return data
    try: 
        if not key:
            key = 'hps'
            if web.ctx.session.get('user'):
                key = web.ctx.session.user['UserCode'] + 'hps'
                             
        k = des(str(key[0:8]), CBC, str(key[0:8]), pad=None, padmode=PAD_PKCS5)     
        d = k.decrypt(binascii.a2b_hex(str(data)))
        return d.decode('GBK') 
    except Exception,ce:
        print ce.message
        return data 
    

def gen_md5_salt():
    '''生成MD5的盐值
    '''
    abc = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars = []
    for i in range(16):
        chars.append(random.choice(abc))
    
    return "".join(chars)


def md5_encrypt(password, salt=None):
    '''md5加密
    '''
    return hashlib.md5(password + salt).hexdigest()  
 
 
def client_rsa_encrypt(data):
    return rsa_encrypt(data, get_client_pub_key())
     
def client_rsa_decrypt(data):    
    return rsa_decrypt(data, get_client_pri_key())

def client_signature(data):
    return signature(data, get_client_pri_key())
 
def client_verify_sign(data, signature):
    return verify_sign(data, signature, get_client_pub_key())

    
def rsa_encrypt(data, pub_key):
    try:
        return binascii.b2a_hex(encrypt(data, pub_key))
    except:
        return data
    
def rsa_decrypt(data, pri_key):
    try:
        return decrypt(binascii.a2b_hex(data), pri_key) 
    except:
        return data


def signature(data, pri_key):
    try:
        return binascii.b2a_hex(sign(data, pri_key, 'SHA-1'))
    except:
        return data

def verify_sign(data, signature, pub_key):
    try:
        return verify(data, binascii.a2b_hex(signature), pub_key)
    except:
        return data
      
def get_client_pub_key(): 
    return PublicKey(9659409811222239424053139659514350094343427389834135540932282496665611583618159590834922783558917852795055561382877564364710885749628173307757081925597489, 65537)

def get_client_pri_key(): 
    return PrivateKey(9659409811222239424053139659514350094343427389834135540932282496665611583618159590834922783558917852795055561382877564364710885749628173307757081925597489, 
                          65537, 
                          1350522179840843795758104867481422553892744940614464866587767284388162395131790899554868688522906461439000088568816762804091645889133667242002096698398417,
                          5559425529932599305598725281545023902835884959815769154010890312251665313855301237,  
                          1737483443067065782717045867372208780049132259225788701387959997763307597)