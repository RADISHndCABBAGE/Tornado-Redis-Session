#coding=utf-8
__author__ = 'karldoenitz'

from ipe.sysu.step2.base import BaseHandler


class HelloHandler(BaseHandler):
    def get(self):
        print(self.session)
        self.write(self.session['key'])
        self.finish()
        #self.render("./templates/hello.html", page_object=l)


class TestGetHandler(BaseHandler):
    def get(self):
        test = self.get_argument('test', '')
        self.session['key'] = "今天玩session玩到晚上11点多"
        self.session.save()
        #将test输出到浏览器上。
        self.write(test)
        self.finish()