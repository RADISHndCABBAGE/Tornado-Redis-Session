class A(object):
    def __init__(self):
        self.demo={}
        return
    def test(self):
        rule={}
        rule['A']='B'
        rule['B']='C'
        print(rule)
        type(rule)
        self.demo[1]=2
        self.demo[2]=3
        print(self.demo)
        type(self.demo)
a = A()
b = None
if b:
    print("nihc")
if a:
    print("haha")
    a.test()

