#coding=utf-8
__author__ = 'karldoenitz'

import tornado.web
from ipe.sysu.step2.session import  Session


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        self.session = Session(self.application.session_manager, self)