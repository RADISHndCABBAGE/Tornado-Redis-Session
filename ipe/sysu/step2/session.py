import hashlib
import hmac
import uuid

import redis
import ujson


class SessionManager(object):
    '''
        初始化，需要redis的地址，端口，密码存储在store_optoins中,获取一个redis类的对象
        secret：用于加密session_id
        store_options：存储建立Redis连接需要的配置信息
        session_timeout：设置session的寿命
    '''
    def __init__(self,secret,store_options,session_timeout):
        self.secret = secret
        self.session_timeout = session_timeout
        try:
            self.redis = redis.StrictRedis(host=store_options['redis_host'],
                                           port=store_options['redis_port']
                                           )
        except Exception as e:
                print(e)
    '''
     _fetch方法根据传入的session_id从SessionManager.redis中获取值，然后将这个值转化为json串，如果值不存在
    则返回空 json {}
    总之：_fetch方法获取的是json串

    '''
    def _fetch(self,session_id):
        try:
            #取出来的raw_data是一个json字符串，我们需要调用ujson.loads返回该字符串的原始数据
            session_data = raw_data = self.redis.get(session_id)
            if raw_data:
                #如果session_id存在值，就重新设置过期时间。
                self.redis.setex(session_id,self.session_timeout,raw_data)
                session_data = ujson.loads(raw_data)
            if isinstance(session_data,dict):
                return session_data
            else:
                return {}
        except IOError:
            return {}
    '''

    '''
    def get(self,request_handler=None):
        if not request_handler:
            session_id = None
            hmac_key = None
        else:
            '''
            从coolie中获取加密的session_id和加密的hmac_key
            '''
            session_id = request_handler.get_secure_cookie("session_id")
            hmac_key = request_handler.get_secure_cookie("verification")
        if not session_id:
            '''
            如果没有session_id则生成一个
            '''
            session_exists = False
            session_id = self._generate_id()
            hmac_key = self._generate_hmac(session_id)
        else:
            session_exists = True
        '''
        用获取到的session_id算一下hmac，检查是否与cookie中的hmac一致
        '''
        check_hmac = self._generate_hmac(session_id)
        '''
        从cookie中取出的是byte类型，而直接生成的session_id和hmac_key是str类型，执行！=操作的时候一定返回false
        '''
        if not session_exists:
            hmac_key = hmac_key.encode('utf-8')
        if hmac_key != check_hmac.encode('utf-8'):
            raise InvalidSessionException()
        '''
        将从cookie中获取到的session_id暗文，和hmac_key暗文封装到sessionData，初始化一个session对象出来
        '''
        session = SessionData(session_id,hmac_key)
        '''
        如果session之前就存在，就通过session_id暗文传入_fetch方法从redis中获取键值对
        python3.5中没有iteritems方 法
        '''
        if session_exists:
            session_data = self._fetch(session_id)
            for key,data in session_data.items():
                session[key] = data
        return session

    def set(self,request_handler,session):
        request_handler.set_secure_cookie("session_id",session.session_id)
        request_handler.set_secure_cookie("verification",session.hmac_key)
        session_data = ujson.dumps(dict(session.items()))
        #print(session_data)
        try:
            self.redis.setex(session.session_id,self.session_timeout,session_data)
        except Exception as e:
            print(e)

    '''
    生成session_id的方法
    '''
    def _generate_id(self):
        new_id = hashlib.sha256(self.secret.encode('utf-8')+str(uuid.uuid4()).encode('utf-8'))
        return new_id.hexdigest()


    def _generate_hmac(self, session_id):
        if isinstance(session_id,bytes):
            return hmac.new(session_id, self.secret.encode('utf-8'), hashlib.sha256).hexdigest()
        else:
            return hmac.new(session_id.encode('utf-8'), self.secret.encode('utf-8'), hashlib.sha256).hexdigest()


class InvalidSessionException(Exception):
    pass




class SessionData(dict):
    def __init__(self,session_id,hmac_key):
        self.session_id = session_id
        self.hmac_key = hmac_key



class Session(SessionData):
    def __init__(self,session_manager,request_handler):
        self.session_manager = session_manager
        self.request_handler = request_handler
        try:
            current_session = session_manager.get(request_handler)
        except InvalidSessionException:
            #如果检查check_hmac与hmac_key不一致，则新建一个session
            print("不一致")
            current_session = session_manager.get()
        for key,data in current_session.items():
            self[key] = data
        self.session_id = current_session.session_id
        self.hmac_key = current_session.hmac_key

    def save(self):
        self.session_manager.set(self.request_handler,self)



