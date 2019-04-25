# 寄存器类
class Register:


    def __init__(self):
        # 寄存器编号
        self.regNum = 0
        # 寄存器的值
        self.value = 0
        # 正在被写
        self.writeSemaphore = 0
        # 正在被读
        self.readSemaphore = 0
        # busy
        self.busy = []
        # wbusyList 等待使用寄存器的队列
        self.w_busy = []
        self.r_busy = []

    # 写寄存器
    def write(self, value):
        # 正在被读写
        # while self.readSemaphore or self.writeSemaphore:
            # print("busying ", self.readSemaphore, " ", self.writeSemaphore)
            # return "busy"

        #锁住
        # self.writeSemaphore = 1
        self.value = value
        # self.writeSemaphore = 0


    # 读寄存器
    def read(self):
        # 正在被读写
        # while self.readSemaphore or self.writeSemaphore:
            # print("busying ", self.readSemaphore, " ", self.writeSemaphore)
            # return "busy"

        # self.readSemaphore = 1
        tempValue = self.value
        # self.readSemaphore = 0
        return tempValue