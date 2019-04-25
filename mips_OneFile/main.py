# import MIPSsim
# import Output
# import Operation
# import Instruction
# import Output



# 三目运算
def iif(condition, true_value, false_value):
    if condition:
        return true_value
    else:
        return false_value

# 写入txt的类
class Output:
    # 定义静态变量实例
    # 双下划线开头的命名形式在 Python 的类成员中使用表示名字改编
    __instance = None
    writeListSim = []
    writeListDis = []

    def __init__(self):
        pass

    # 打印并存在数组中 printAndSaveSimulation printAndSaveDisassembly
    def pasSim(self, str):
        print(str)
        self.writeListSim.append(str)

    def pasDis(self, str):
        print(str)
        self.writeListDis.append(str)

    # 数组写入文件
    def writeSimulation(self, fileName):
        f = open(fileName, 'w')
        for line in self.writeListSim:
            f.write(line)

    def writeDisassembly(self, fileName):
        f = open(fileName, 'w')
        for line in self.writeListDis:
            f.write(line)
            f.write('\n')

slingleton = Output()


# 执行操作的类
class Operation:

    def ex_NOP(ins, regList):
        ins.nextPC += 4

    def ex_ADD(ins, regList):
        regList[int(ins.rd, 2)] = regList[int(ins.rs, 2)] + regList[int(ins.rt, 2)]

    def ex_SUB(ins, regList):
        regList[int(ins.rd, 2)] = regList[int(ins.rs, 2)] - regList[int(ins.rt, 2)]

    def ex_MUL(ins, regList):
        regList[int(ins.rd, 2)] = regList[int(ins.rs, 2)] * regList[int(ins.rt, 2)]

    def ex_AND(ins, regList):
        regList[int(ins.rd, 2)] = regList[int(ins.rs, 2)] & regList[int(ins.rt, 2)]

    def ex_OR(ins, regList):
        regList[int(ins.rd, 2)] = regList[int(ins.rs, 2)] | regList[int(ins.rt, 2)]

    def ex_XOR(ins, regList):
        regList[int(ins.rd, 2)] = regList[int(ins.rs, 2)] ^ regList[int(ins.rt, 2)]

    def ex_NOR(ins, regList):
        regList[int(ins.rd, 2)] = ~(regList[int(ins.rs, 2)] | regList[int(ins.rt, 2)])

    def ex_SLT(self,ins, regList):
        regList[int(ins.rd, 2)] = self.iif(regList[int(ins.rs, 2)] < regList[int(ins.rt, 2)], 1, 0)

    def ex_ADDI(ins, regList):
        regList[int(ins.rt, 2)] = regList[int(ins.rs, 2)] + int(ins.immediate, 2)

    def ex_ANDI(ins, regList):
        regList[int(ins.rd, 2)] = regList[int(ins.rs, 2)] & int(ins.immediate, 2)

    def ex_ORI(ins, regList):
        regList[int(ins.rd, 2)] = regList[int(ins.rs, 2)] | int(ins.immediate, 2)

    def ex_XORI(ins, regList):
        regList[int(ins.rd, 2)] = regList[int(ins.rs, 2)] ^ int(ins.immediate, 2)

    # 部分需要左移两位+"00"
    def ex_J(ins, regList):
        ins.nextPC = int(ins.immediate + "00", 2)

    def ex_JR(ins, regList):
        ins.nextPC = int(ins.rs + "00", 2)

    # 相等则+offset左移2位跳转
    def ex_BEQ(ins, regList):
        offset = iif(regList[int(ins.rs, 2)] == regList[int(ins.rt, 2)], int(ins.offset + "00", 2), 0)
        ins.nextPC += offset

    # rs<0跳转
    def ex_BLTZ(ins, regList):
        offset = iif(regList[int(ins.rs, 2)] < 0, int(ins.offset + '00', 2), 0)
        ins.nextPC += offset

    # rs>0跳转
    def ex_BGTZ(ins, regList):
        offset = iif(regList[int(ins.rs, 2)] > 0, int(ins.offset + '00', 2), 0)
        ins.nextPC += offset

    def ex_BREAK(ins, regList):
        ins.nextPC = -1

    # SW memory[base+offset] = rt 与LW反向赋值
    def ex_SW(ins, regList, memDic):
        memoryAddress = str(regList[int(ins.base, 2)] + int(ins.offset, 2))
        num = regList[int(ins.rt, 2)]
        memDic[memoryAddress] = regList[int(ins.rt, 2)]

    # LW rt = memory[base+offset] base是对应寄存器里面的值  340(R16)
    def ex_LW(ins, regList, memDic):
        # memory地址
        memoryAddress = str(regList[int(ins.base, 2)] + int(ins.offset, 2))
        regList[int(ins.rt, 2)] = memDic[memoryAddress]

    # SLL rd = rt << shiftAmt
    def ex_SLL(ins, regList):
        mask = (2 ** 32) - 1
        # 左移会有溢出
        regList[int(ins.rd, 2)] = (regList[int(ins.rt, 2)] << int(ins.sa, 2)) & mask

    # SRL rd = rt >> sa
    def ex_SRL(ins, regList):
        regList[int(ins.rd, 2)] = (regList[int(ins.rt, 2)] >> int(ins.sa, 2))

    # SRA rd = rt >> sa
    def ex_SRA(ins, regList):
        regList[int(ins.rd, 2)] = (regList[int(ins.rt, 2)] >> int(ins.sa, 2))



# 指令类
class Instruction:
    # tag = 0 打印反汇编  tag = 1 打印执行过程
    printDisOrSimtag = 0
    # 操作名称
    opName = ''
    # 操作码
    op = ''
    # 标识
    identification = ''
    # 目标
    target = ''
    # 偏移量
    offset = ""
    # 从寄存器取
    base = ""
    # 移位
    sa = ""
    # 源寄存器
    rs = ""
    # 目标寄存器
    rt = ""
    # 寄存器
    rd = ""
    # 立即数
    immediate = ""
    # 移位数
    shiftAmt = ""
    # offset
    offset = ""
    #剩余
    lastStr = ''
    # 打印类型
    printTag = 0
    # 当前指令地址
    currentPC = 0
    # 下条指令地址
    nextPC = 0
    # 指令计数
    cycle = 0
    # 01指令字符串
    line = ''
    # index
    instr_index = ''
    # 打印本条指令 1:op rs rt rd   2:op rs rt imm   3:op index
    # tag = 0 打印反汇编  tag = 1 打印执行过程
    def printInstruction(self,tag):
        global printDisOrSimtag
        printDisOrSimtag = tag
        if self.printTag == "OpRsRtRd":
            return self.print_ins_OpRsRtRd()
        elif self.printTag == "OpRsRtImm":
            return self.print_ins_OpRsRtImm()
        elif self.printTag == "OpRsRtOffsetLS":
            return self.print_ins_OpRsRtOffsetLS()
        elif self.printTag == "OpIndex":
            return self.print_ins_OpIndex()
        elif self.printTag == "OpRsOffset":
            return self.print_ins_OpRsOffset()
        elif self.printTag == "OpRsMem":
            return self.print_ins_OpRsMem()
        elif self.printTag == "OpRs":
            return self.print_ins_OpRs()
        elif self.printTag == "OpRdRtSa":
            return self.print_ins_OpRdRtSa()
        elif self.printTag == "Op":
            return self.print_ins_Op()
        Output.slt.pasDis('\n')


    # 拼接寄存器名称
    def appendRegName(self,regStr):
        return "R" + str(int(regStr, 2))

    def print_ins_Op(self):
        insStr = str(self.currentPC) + ' ' + self.opName
        if printDisOrSimtag:
            return self.line+'\t'+insStr
        else:
            return ('Cycle:' + str(self.cycle) + ' ' + insStr)
    def print_ins_OpRs(self):
        rs = self.appendRegName(self.rs)
        rt = self.appendRegName(self.rt)
        rd = self.appendRegName(self.rd)
        insStr = str(self.currentPC) + ' ' + self.opName + " " + rs
        if printDisOrSimtag:
            return (self.line+'\t'+insStr)
        else:
            return ('Cycle:' + str(self.cycle) + ' ' + insStr)
    # 打印指令 op rs rt rd 类型
    def print_ins_OpRsRtRd(self):
        rs = self.appendRegName(self.rs)
        rt = self.appendRegName(self.rt)
        rd = self.appendRegName(self.rd)
        insStr = str(self.currentPC) + ' ' + self.opName+" "+rd+"," + rs + "," +rt
        if printDisOrSimtag:
            return (self.line+'\t'+insStr)
        else:
            return ('Cycle:' + str(self.cycle) + ' '+ insStr)

    # 打印指令 op rs rt immediate 类型
    def print_ins_OpRsRtImm(self):
        rs = self.appendRegName(self.rs)
        rt = self.appendRegName(self.rt)
        immediate = "#"+str(int(self.immediate, 2))
        insStr = str(self.currentPC) + ' ' + self.opName + " " + rt +"," + rs + "," +immediate
        if printDisOrSimtag:
            return (self.line+'\t'+insStr)
        else:
            return ('Cycle:' + str(self.cycle) + ' ' + insStr)

    # 打印指令 op rs rt immediate左移2位 类型
    def print_ins_OpRsRtOffsetLS(self):
        rs = self.appendRegName(self.rs)
        rt = self.appendRegName(self.rt)
        offset = "#"+str(int(self.offset+'00', 2))
        insStr = str(self.currentPC) + ' ' + self.opName + " " + rs +',' + rt + ',' +offset
        if printDisOrSimtag:
            return (self.line+'\t'+insStr)
        else:
            return ('Cycle:' + str(self.cycle) + ' ' +insStr)

    # 打印指令 op rs rt sa 类型
    def print_ins_OpRdRtSa(self):
        rd = self.appendRegName(self.rd)
        rt = self.appendRegName(self.rt)
        sa = '#'+str(int(self.sa,2))
        insStr = str(self.currentPC) + ' ' + self.opName + " " + rd +"," + rt + "," +sa
        if printDisOrSimtag:
            return (self.line+'\t'+insStr)
        else:
            return ('Cycle:' + str(self.cycle) + ' ' + insStr)

    # 打印指令 op rs  offset 类型
    def print_ins_OpRsOffset(self):
        rs = self.appendRegName(self.rs)
        offset = "#"+str(int(self.offset+'00', 2))
        insStr = str(self.currentPC) + ' ' + self.opName+" "+rs+ "," +offset
        if printDisOrSimtag:
            return (self.line+'\t'+insStr)
        else:
            return ('Cycle:' + str(self.cycle) + ' ' + insStr)

    # 打印指令 op rs  offset(Rbase) 类型  rt ← memory[base+offset]
    def print_ins_OpRsMem(self):
        rt = self.appendRegName(self.rt)
        offset = str(int(self.offset, 2))
        Rbase = '(R'+str(int(self.base,2))+')'
        insStr = str(self.currentPC) + ' ' + self.opName+" "+rt+ "," +offset+Rbase
        if printDisOrSimtag:
            return (self.line+'\t'+insStr)
        else:
            return ('Cycle:' + str(self.cycle) + ' ' + insStr)

    # 打印指令 op index 类型
    def print_ins_OpIndex(self):
        x = eval("0b" + self.instr_index+'00')
        instr_index = "#"+str(x)
        insStr = str(self.currentPC) + ' ' + self.opName + " " + instr_index
        if printDisOrSimtag:
            return (self.line+'\t'+insStr)
        else:
            return ('Cycle:' + str(self.cycle) + ' ' + insStr)



# 反汇编和执行汇编
class MIPSsim:

    # 01指令码对应指令
    ins2BinaryDic = {
        # Category-1
        # J target
        '010000': 'J',
        # JR rs
        '010001': 'JR',
        # BEQ rs,rt,#offset
        '010010': 'BEQ',
        # BLTZ rs,#offset
        '010011': 'BLTZ',
        # BGTZ rs,#offset
        '010100': 'BGTZ',
        # break
        '010101': 'BREAK',
        # SW rt,offset(base)
        '010110': 'SW',
        # LW rt,offset(base)
        '010111': 'LW',
        # SLL rd,rt,#sa
        '011000': 'SLL',
        # SRL rd,rt,#sa
        '011001': 'SRL',
        # SRA rd,rt,#sa
        '011010': 'SRA',
        # NOP
        '011011': 'NOP',

        # Category-2
        # op rd,rs,rt
        '110000': 'ADD',
        '110001': 'SUB',
        '110010': 'MUL',
        '110011': 'AND',
        '110100': 'OR',
        '110101': 'XOR',
        '110110': 'NOR',
        '110111': 'SLT',

        # 立即数
        # op rt,rs,#immediate
        '111000': 'ADDI',
        '111001': 'ANDI',
        # op rt,rs,immediate
        '111010': 'ORI',
        '111011': 'XORI',
    }
    # 初始化指令list
    insSequenceDic = {}
    # 初始化反汇编内容
    insDisassemblyList = []
    # 初始化寄存器list
    regList = [0 for i in range(32)]
    # memList memDic
    memList = []
    memDic = {}
    cycle = 1

    def __init__(self):

        self.ins2BinaryDic = {
            # Category-1
            # J target
            '010000': 'J',
            # JR rs
            '010001': 'JR',
            # BEQ rs,rt,#offset
            '010010': 'BEQ',
            # BLTZ rs,#offset
            '010011': 'BLTZ',
            # BGTZ rs,#offset
            '010100': 'BGTZ',
            # break
            '010101': 'BREAK',
            # SW rt,offset(base)
            '010110': 'SW',
            # LW rt,offset(base)
            '010111': 'LW',
            # SLL rd,rt,#sa
            '011000': 'SLL',
            # SRL rd,rt,#sa
            '011001': 'SRL',
            # SRA rd,rt,#sa
            '011010': 'SRA',
            # NOP
            '011011': 'NOP',

            # Category-2
            # op rd,rs,rt
            '110000': 'ADD',
            '110001': 'SUB',
            '110010': 'MUL',
            '110011': 'AND',
            '110100': 'OR',
            '110101': 'XOR',
            '110110': 'NOR',
            '110111': 'SLT',

            # 立即数
            # op rt,rs,#immediate
            '111000': 'ADDI',
            '111001': 'ANDI',
            # op rt,rs,immediate
            '111010': 'ORI',
            '111011': 'XORI',
        }




    # 反汇编
    @classmethod
    def disassemble(self,fileName):

        f = open(fileName, "r")
        line = f.readline()
        address = 256
        while line:
            opetation = line[0:6]
            if opetation not in self.ins2BinaryDic.keys():
                # 非指令 即为内存
                # 补码
                if line[0]=='1':
                    memoryValue = int(line, 2)- (1<<32)
                else:
                    memoryValue = int(str(line), 2)

                # list 按顺序存地址  dic 存地址加内容
                self.memList.append(str(address))
                self.memDic[str(address)] = memoryValue
                memStr = line.strip('\n') + '\t' + str(memoryValue)
                slingleton.pasDis(memStr)
                line = f.readline()
                address += 4
                continue

            # 指令
            ins = Instruction()
            ins.line = line.strip('\n')
            opName = self.ins2BinaryDic[opetation]

            # category1 op index
            if opName in ['J']:
                ins.opName = opName
                ins.printTag = "OpIndex"
            # op rs
            elif opName in ['JR']:
                ins.opName = opName
                ins.printTag = "OpRs"
            # category2 op rs rt 立即数
            elif opName in ['ADDI', 'ANDI', 'ORI', 'XORI']:
                ins.opName = opName
                ins.printTag = "OpRsRtImm"

            # category2 op rs rt offset左移2位
            elif opName in ['BEQ']:
                ins.opName = opName
                ins.printTag = "OpRsRtOffsetLS"
            # category2 op rs rt 立即数左移2位
            elif opName in ['SLL','SRL','SRA']:
                ins.opName = opName
                ins.printTag = "OpRdRtSa"
            # category2 op rs rt 立即数左移2位
            elif opName in ['BGTZ','BLTZ']:
                ins.opName = opName
                ins.printTag = "OpRsOffset"

            # category2 op rs rt rd
            elif opName in ['ADD','SUB','MUL','AND','OR','XOR','NOR','SLT']:
                # 判断操作码
                ins.opName = opName
                ins.printTag = "OpRsRtRd"
            # 移位
            elif opName in ['LW', 'SW']:
                ins.opName = opName
                ins.printTag = "OpRsMem"
            # op
            elif opName in ['NOP', 'BREAK']:
                ins.opName = opName
                ins.printTag = "Op"
            ins.op = opetation
            ins.rs = line[6:11]
            ins.rt = line[11:16]
            ins.rd = line[16:21]
            ins.sa = line[21:26]
            ins.base = line[6:11]
            # immediate
            ins.immediate = line[16:32]
            # 剩余内容
            ins.lastStr = line[21:32]
            # 跳转指令地址
            ins.instr_index = line[6:32]
            # 移位
            ins.shiftAmt = line[21:26]
            # offset
            ins.offset = line[16:32]
            # 地址
            ins.currentPC = address
            # 指令和指令地址存入字典
            self.insSequenceDic[str(address)] = ins

            slingleton.pasDis(ins.printInstruction(1))
            address += 4

            line = f.readline()

    # 顺序执行指令
    @classmethod
    def excuteInsSequential(self,address):
        while address != -1:
            address = self.excuteIns(self,address)

    # 执行具体的指令
    def excuteIns(self,address):
        ins = self.insSequenceDic[str(address)]
        ins.cycle = self.cycle
        slingleton.pasSim('--------------------\n')
        slingleton.pasSim(ins.printInstruction(0))
        ins.currentPC = address
        ins.nextPC = address + 4

        if ins.opName == "NOP":
            Operation.ex_NOP(ins,self.regList)
        elif ins.opName == "ADD":
            Operation.ex_ADD(ins,self.regList)
        elif ins.opName == "SUB":
            Operation.ex_SUB(ins, self.regList)
        elif ins.opName == "MUL":
            Operation.ex_MUL(ins, self.regList)
        elif ins.opName == "AND":
            Operation.ex_AND(ins, self.regList)
        elif ins.opName == "OR":
            Operation.ex_OR(ins, self.regList)
        elif ins.opName == "XOR":
            Operation.ex_XOR(ins, self.regList)
        elif ins.opName == "NOR":
            Operation.ex_NOR(ins, self.regList)
        elif ins.opName == "SLT":
            Operation.ex_SLT(ins, self.regList)
        elif ins.opName == "ADDI":
            Operation.ex_ADDI(ins, self.regList)
        elif ins.opName == "ANDI":
            Operation.ex_ANDI(ins, self.regList)
        elif ins.opName == "ORI":
            Operation.ex_ORI(ins, self.regList)
        elif ins.opName == "XORI":
            Operation.ex_XORI(ins, self.regList)

        elif ins.opName == "J":
            Operation.ex_J(ins, self.regList)
        elif ins.opName == "JR":
            Operation.ex_JR(ins, self.regList)
        elif ins.opName == "BEQ":
            Operation.ex_BEQ(ins, self.regList)
        elif ins.opName == "BLTZ":
            Operation.ex_BLTZ(ins, self.regList)
        elif ins.opName == "BGTZ":
            Operation.ex_BGTZ(ins, self.regList)
        elif ins.opName == "BREAK":
            Operation.ex_BREAK(ins, self.regList)
        elif ins.opName == "SW":
            Operation.ex_SW(ins, self.regList, self.memDic)
        elif ins.opName == "LW":
            Operation.ex_LW(ins, self.regList, self.memDic)
        elif ins.opName == "SLL":
            Operation.ex_SLL(ins, self.regList)
        elif ins.opName == "SRL":
            Operation.ex_SRL(ins, self.regList)
        elif ins.opName == "SRA":
            Operation.ex_SRA(ins, self.regList)

        # Output.slt.pas()('nextPC',ins.nextPC)
        self.cycle += 1

        self.printRegList(self,self.regList,self.memList)
        return ins.nextPC


    # 打印regList,memList
    def printRegList(self,regList,memList):
        slingleton.pasSim('\n\nRegisters\n')
        str1 = 'R00:'
        for i in range(0,8):
            str1 = str1 +'\t'+ str(regList[i])
        str2 = 'R08:'
        for i in range(8,16):
            str2 = str2 + '\t' + str(regList[i])
        str3 = 'R16:'
        for i in range(16,24):
            str3 = str3 + '\t' + str(regList[i])
        str4 = 'R24:'
        for i in range(24,32):
            str4 = str4 + '\t' + str(regList[i])

        slingleton.pasSim(str1+'\n')
        slingleton.pasSim(str2+'\n')
        slingleton.pasSim(str3+'\n')
        slingleton.pasSim(str4+'\n')
        slingleton.pasSim('\n')
        slingleton.pasSim('Data\n')

        str1 = '340:'
        for i in range(8):
            str1 = str1 + '\t' + str(self.memDic[memList[i]])

        str2 = '372:'
        for i in range(8):
            str2 = str2 + '\t' + str(self.memDic[memList[i + 8]])
        str3 = '404:'
        for i in range(8):
            str3 = str3 + '\t' + str(self.memDic[memList[i + 16]])

        slingleton.pasSim(str1+'\n')
        slingleton.pasSim(str2+'\n')
        slingleton.pasSim(str3+'\n')





if __name__ == '__main__':
    fileName = input("请输入文件名:\n")
    MIPSsim.disassemble(fileName)
    MIPSsim.excuteInsSequential(256)
    slingleton.writeSimulation('simulation.txt')
    slingleton.writeDisassembly('disassembly.txt')

