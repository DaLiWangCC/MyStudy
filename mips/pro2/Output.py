
class Singleton(object):

    # 定义静态变量实例
    # 双下划线开头的命名形式在 Python 的类成员中使用表示名字改编
    __instance = None
    writeListSim = []
    writeListDis = []
    def __init__(self):
        pass

    # 类方法 cls表示类本身
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    # 打印并存在数组中 printAndSaveSimulation printAndSaveDisassembly
    def pasSim(self,str):
        print(str)
        self.writeListSim.append(str)
    def pasDis(self,str):
        print(str)
        self.writeListDis.append(str)

    # 数组写入文件
    def writeSimulation(self,fileName):
        f = open(fileName,'w')
        for line in self.writeListSim:
            f.write(line)

    def writeDisassembly(self,fileName):
        f = open(fileName,'w')
        for line in self.writeListDis:
            f.write(line)
            f.write('\n')


slt = Singleton()

if __name__ == "__main__":
    instance2 = Singleton()
    # instance1.writeList = ['hhh']

    # print (id(instance1))
    # print (id(instance2))
    # print(instance1.writeList)
    # print(instance1.writeList)