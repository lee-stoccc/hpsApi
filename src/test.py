#coding UTF-8
import sqlalchemy
import sqlalchemy.orm


def debug(func):
    def wrapper(*args, **kwargs):
        print "[DEBUG]: enter {}()".format(func.__name__)
        return func(*args, **kwargs)
    return wrapper

# @debug
def do1(*args, **kwargs):
    a = list(args);
    print a

class A(object):
    #HotelCode = "aaaa"
    def __init__(self):
        self.HotelID = 0
        self.HotelName = ""

    def Do1(self, *params):
        do1(10, 20)
        aryTemp = list(params)
        return aryTemp

    def Do2(self):
        engine = sqlalchemy.create_engine("mysql+mysqldb://tam:123456@10.3.15.75:3306/hps")



# a = A()
# a.HotelCode = "ffff"
# print "%s" % (a.Do1(1, 2, 3))


def one(*x):
    print type(x)
    for a in x:
        print(a)

lst=["abc",123,"www.qingsword.com"]
stri="abcd"

