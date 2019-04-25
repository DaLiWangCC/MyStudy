from enum import Enum
import Instruction
import Output
import queue
import ctypes
import copy

from pro2 import Register

# flag 标记单元是否正在被使用
IF_flag = 0
issue_flag = 0
MEM_flag = 0
WB_flag = 0
break_flag = 0
PC_num = 256 # PC
cycleLock = 0
memBusy = [] # 内存繁忙队列
insNum = 0 # 指令次序编号

waitingIF = 0  # 等待IF
executedIF = 0 # 执行IF
tempIF = 0 # 临时IF


# 数组模拟队列
class myQueue:
    def __init__(self):
        # 寄存器编号
        self.list = []

    # getl
    def getl(self):
        if len(self.list):
            temp = self.list[0]
            del self.list[0]
            return temp
    # putl
    def putl(self,value):
        self.list.append(value)
    # 判满
    def fulll(self,size):
        if len(self.list)>=size:
            return 1
        else:
            return 0
    # 判空
    def emptyl(self):
        if len(self.list):
            return 0
        else:
            return 1


# pre-issue 队列
Pre_issue = queue.Queue(4)
Pre_issue = myQueue()
# fetch unit停滞
stalled = 0

# LW SW 指令
Pre_ALU1 = queue.Queue(2)
Pre_ALU1 = myQueue()
# 非内存操作指令
Pre_ALU2 = queue.Queue(2)
Pre_ALU2 = myQueue()
Pre_MEM = queue.Queue(1)
Pre_MEM = myQueue()
Post_MEM = queue.Queue(1)
Post_MEM = myQueue()
Post_ALU2 = queue.Queue(1)
Post_ALU2 = myQueue()
Post_MEM = queue.Queue(1)
Post_MEM = myQueue()

# 指令和2进制
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
# 寄存器list


# 初始化指令list  指令翻译成汇编后以  地址：指令的kv形式存入字典
insSequenceDic = {}
# 初始化反汇编内容
insDisassemblyList = []
# 初始化寄存器list
regList = []
# memList 内存地址的list   memDic 内存地址对应的值
memList = []
memDic = {}

# 初始化全局变量
def initData():
    for i in range(0,32):
        register = Register.Register()
        register.regNum = i
        regList.append(register)

# 反汇编
def disassemble(fileName):

    f = open(fileName, "r")
    line = f.readline()
    PC_num = 256
    i = 0
    while line:
        i += 1
        opetation = line[0:6]
        # 非指令 即为内存
        if opetation not in ins2BinaryDic.keys():
            # 补码
            if line[0]=='1':
                memoryValue = int(line, 2)- (1<<32)
            else:
                memoryValue = int(str(line), 2)

            # list 按顺序存地址  dic 存地址加内容
            memList.append(str(PC_num))
            memDic[str(PC_num)] = memoryValue
            memStr = line.strip('\n') + '\t' + str(memoryValue)
            Output.slt.pasDis(memStr)
            line = f.readline()
            PC_num += 4
            continue
        else:
            # 指令
            ins = Instruction.Instruction()
            ins.line = line.strip('\n')
            opName = ins2BinaryDic[opetation]

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
            ins.currentPC = PC_num
            # 指令和指令地址存入字典
            insSequenceDic[str(PC_num)] = ins
            # 指令地址
            ins.address = PC_num

            # 打印并写入文件
            Output.slt.pasDis(ins.printInstruction(1))
            # 取址+4
            PC_num += 4
            line = f.readline()

# 顺序执行指令,每次取出两条，放进pre-issue（能放4个）
def excuteInsSequential(num):
    global PC_num
    PC_num = num
    global cycleLock
    global break_flag
    # 一个时钟周期下
    i = 0
    while not break_flag or not Pre_issue.emptyl() or not Pre_ALU1.emptyl() or not Pre_ALU2.emptyl() or not Pre_MEM.emptyl() or not Post_ALU2.emptyl() or not Post_MEM.emptyl():
        i += 1
        cycleLock = i
        # print('cycle ', i ,' ',PC_num) 调试用
        # 每次顺序执行IF取两个指令
        if_insArray = IF_exc()
        # 乱序issue两个指令
        is_ins1 = issue_exc(1)
        is_ins0 = issue_exc(0)

        alu_ins1 = ALU_exc(1)
        alu_ins0 = ALU_exc(0)
        mem_ins = MEM_exc()
        WB(0)
        WB(1)

        # 在时钟周期末IF结果写入队列
        global insNum
        if if_insArray:
            for if_ins in if_insArray:
                if not Pre_issue.fulll(4):
                    insNum += 1
                    if_ins.insNum = insNum
                    Pre_issue.putl(if_ins)


        # 时钟周期末issue成功的结果写入队列 Pre_ALU1 为内存指令  1:内存指令  0:非内存
        if not Pre_ALU1.fulll(2) and is_ins1 and is_ins1.type:
            Pre_ALU1.putl(is_ins1)
            # 释放该指令读的寄存器
            scoreBoard(is_ins1, 1)

        if not Pre_ALU2.fulll(2) and is_ins0 and not is_ins0.type:
            Pre_ALU2.putl(is_ins0)
            # 释放该指令读的寄存器
            scoreBoard(is_ins0, 1)


        # 在时钟周期末把ALU结果写入post
        if not Post_ALU2.fulll(1) and alu_ins0:
            Post_ALU2.putl(alu_ins0)
        if not Pre_MEM.fulll(1) and alu_ins1:
            Pre_MEM.putl(alu_ins1)

        # 时钟周期末把MEM结果写入Post-MEM
        if mem_ins:
            Post_MEM.putl(mem_ins)

        # 周期末尾打印
        printQueue(i)
# 取指令译码
def IF_exc():
    # Break 不再IF
    if break_flag:
        return 0
    global stalled
    global PC_num
    global waitingIF
    global executedIF
    global tempIF
    insArray = []

# 如果有wait的分支指令
    if executedIF:
        executedIF = 0
    if waitingIF:
        if checkRegReady(waitingIF):
            excuteIns(waitingIF)
            executedIF = waitingIF
            # print("if阶段 executedIF", waitingIF.description)
            waitingIF = 0
            return 0
        else:
            # print("if阶段 waitingIF", waitingIF.description)
            return 0
    elif tempIF:
        excuteIns(tempIF)
        executedIF = tempIF
        tempIF = 0
        return 0
    # 有分支指令阻拦
    if stalled:
        return 0

    # 取出第一条指令
    ins1 = insSequenceDic[str(PC_num)]
    # print("if阶段 取第一个指令",ins1.description)

    # 如果第一条不是分支指令，fetch第二条
    if ins1.opName not in ["J","JR","BEQ","BLTZ","BGTZ","BREAK"]:
        if Pre_issue.fulll(4):
            return 0
        insArray.append(ins1)
        PC_num += 4
        ins2 = insSequenceDic[str(PC_num)]
        # print("if阶段 取第二个指令", ins2.description)
        scoreBoard(ins1, 0)
        if not Pre_issue.fulll(4) and not stalled:
            PC_num += 4
            # 如果第二条是branch指令，那么之后暂时不fetch指令，stalled，在分支指令执行后解锁stalled
            # 检查branch指令需要访问的register是否可用
            if ins2.opName in ["J", "JR", "BEQ", "BLTZ", "BGTZ", "BREAK"]:
                stalled = 1
                # 此周期IF/DE branch指令 下个cycle在IF中处理branch指令
                if checkRegReady(ins2):
                    if len(Pre_issue.list) <= 2:
                        executedIF = ins2
                        excuteIns(ins2)
                    else:
                        tempIF = ins2
                    # print('跳转指令可执行')
                else:
                    waitingIF = ins2
            # 第二条不是branch
            else:
                if len(Pre_issue.list) <= 2:
                    insArray.append(ins2)
                    scoreBoard(ins2,0)
                else:
                    PC_num -= 4
                    # print("if阶段 第二个指令 放不进去", ins2.description)

            return insArray
    # 第一条是branch就不fetch第二条
    else:
        PC_num += 4
        stalled = 1
        # 此周期IF/DE branch指令 下个cycle在IF中处理branch指令
        if checkRegReady(ins1):
            executedIF = ins1
            excuteIns(ins1)
        else:
            waitingIF = ins1

        return 0

    return insArray

# 检查指令的寄存器是否准备好
def checkRegReady(ins):
    global memBusy

    # 分支指令
    if ins.opName == 'BEQ':
        rs_reg = regList[int(ins.rs, 2)]
        rt_reg = regList[int(ins.rt, 2)]

        if len(rs_reg.w_busy)==0 and len(rt_reg.w_busy)==0:
            return 1
        else:
            return 0
    if ins.opName == 'JR':
        rs_reg = regList[int(ins.rs, 2)]
        if not rs_reg.busy:
            return 1
        else:
            return 0
    if ins.opName in ['BLTZ','BGTZ']:
        rs_reg = regList[int(ins.rs, 2)]
        if len(rs_reg.w_busy)==0:
            return 1
        else:
            return 0
    if ins.opName in ['J','BREAK','NOP']:
        return 1

    # 内存指令 取base对应的寄存器
    # load 读base指向的寄存器 写rt
    if ins.opName == "LW" :
        rt_reg = regList[int(ins.rt, 2)]
        base_reg = regList[int(ins.base, 2)]
        mem_add = 0
        base_add = 0
        rt_w_add = 0
        rt_r_add = 0

        # 不能在读之前有写的指令
        if len(base_reg.w_busy):
            dic = base_reg.w_busy[0]
            if dic['ins'].insNum < ins.insNum:
                base_add = 1


        # 遍历，在LW前不能有SW，LW可以乱序
        for dic in memBusy:
            add = dic['add']
            type = dic['type']
            if add == ins.address:
                mem_add = 1
                break
            elif type == 'SW':
                mem_add = 0
                break

        if len(rt_reg.w_busy):
            rt_w_add = rt_reg.w_busy[0]['add']
        if len(rt_reg.r_busy):
            rt_r_add = rt_reg.r_busy[0]['add']

        if mem_add and (rt_r_add == 0 or rt_r_add == ins.address) and (rt_w_add == 0 or rt_w_add == ins.address) and base_add == 0:
            return 1
        else:
            return 0
    # store 读rt base
    elif ins.opName == "SW":
        # 要读取的寄存器
        rt_reg = regList[int(ins.rt, 2)]
        base_reg = regList[int(ins.base, 2)]
        rt_add = 0
        base_add = 0
        # 不能在读之前有写的指令
        if len(base_reg.w_busy):
            dic = base_reg.w_busy[0]
            if dic['ins'].insNum < ins.insNum:
                base_add = 1
        # 不能在读之前有写的指令
        if len(rt_reg.w_busy):
            dic = rt_reg.w_busy[0]
            if dic['ins'].insNum < ins.insNum:
                rt_add = 1
        mem_add = 0
        if len(memBusy):
            dic = memBusy[0]
            if dic['ins'].insNum < ins.insNum:
                mem_add = 1
        if mem_add==0 and base_add==0 and rt_add==0:
            return 1
        else:
            return 0
    # 读 rs rt 写rd  rs rt 不能被写占用  rd 不能读或写占用
    elif ins.opName in ["ADD", "SUB", "MUL", "AND", "OR", "XOR", "NOR", "SLT"]:

        # 要读取的寄存器
        rs_reg = regList[int(ins.rs, 2)]
        rt_reg = regList[int(ins.rt, 2)]
        rs_w_add = 0
        rt_w_add = 0

        # 不能在读之前有写的指令
        if len(rs_reg.w_busy):
            dic = rs_reg.w_busy[0]
            if dic['ins'].insNum < ins.insNum:
                rs_w_add = 1
        if len(rt_reg.w_busy):
            dic = rt_reg.w_busy[0]
            if dic['ins'].insNum < ins.insNum:
                rt_w_add = 1

        # 要写入的寄存器编号
        rd_reg = regList[int(ins.rd, 2)]
        rd_w_add = 0
        rd_r_add = 0

        if len(rd_reg.r_busy):
            rd_r_add = rd_reg.r_busy[0]['add']
        if len(rd_reg.w_busy):
            rd_w_add = rd_reg.w_busy[0]['add']

        if rt_w_add == 0 and (rs_w_add == 0) and (rd_w_add == 0 or rd_w_add == ins.address) and (rd_r_add == 0 or rd_r_add == ins.address):
            return 1
        else:
            return 0

    # 读rt 写rd
    elif ins.opName in ["SLL", "SRA", "SRL"]:
        rt_reg = regList[int(ins.rt, 2)]
        rd_reg = regList[int(ins.rd, 2)]

        rt_w_add = 0
        # 不能在读之前有写的指令
        if len(rt_reg.w_busy):
            dic = rt_reg.w_busy[0]
            if dic['ins'].insNum < ins.insNum:
                rt_w_add = 1

        rd_w_add = 0
        rd_r_add = 0
        if len(rd_reg.r_busy):
            rd_r_add = rd_reg.r_busy[0]['add']
        if len(rd_reg.w_busy):
            rd_w_add = rd_reg.w_busy[0]['add']

        # 在寄存器不busying时读取值
        if (rt_w_add == 0) and (rd_w_add == 0 or rd_w_add == ins.address) and (rd_r_add == 0 or rd_r_add == ins.address):
            return 1
        else:
            return 0
    # 取rs 写rt或rd
    elif ins.opName in ["ADDI", "ANDI", "ORI", "XORI"]:

        rs_reg = regList[int(ins.rs, 2)]
        rt_reg = regList[int(ins.rt, 2)]
        rd_reg = regList[int(ins.rd, 2)]
        rs_w_add = 0
        # 不能在读之前有写的指令
        if len(rs_reg.w_busy):
            dic = rs_reg.w_busy[0]
            if dic['ins'].insNum < ins.insNum:
                rs_w_add = 1

        rd_w_add = 0
        rd_r_add = 0
        rt_w_add = 0
        rt_r_add = 0

        if len(rt_reg.w_busy):
            rt_w_add = rt_reg.w_busy[0]['add']
        if len(rd_reg.w_busy):
            rd_w_add = rd_reg.w_busy[0]['add']
        if len(rt_reg.r_busy):
            rt_r_add = rt_reg.r_busy[0]['add']
        if len(rd_reg.r_busy):
            rd_r_add = rd_reg.r_busy[0]['add']

        if ins.opName == 'ADDI':# 写入rt
            if (rt_w_add == 0 or rt_w_add == ins.address) and (rt_r_add == 0 or rt_r_add == ins.address) and rs_w_add == 0:
                return 1
            else:
                return 0
        else:#写入rd
            if (rd_w_add == 0 or rd_w_add == ins.address) and (rd_r_add == 0 or rd_r_add == ins.address) and rs_w_add == 0:
                return 1
            else:
                return 0

# IF decode后 要读取或写入寄存器加入busy队列 type:0 占用  1:读占用释放  2:写占用释放
def scoreBoard(ins,type):
    global memBusy
    # 内存指令 取base对应的寄存器
    # load 写入rt
    if ins.opName == "LW":
        # 要写入的寄存器编号 设置寄存器为忙碌
        ins.write_reg_num = int(ins.rt, 2)
        rt_reg = regList[int(ins.rt, 2)]
        # 从base_reg读
        base_reg = regList[int(ins.base, 2)]
        # 要读取的内存地址 base + offset
        ins.mem_value = str(regList[int(ins.base, 2)].value + int(ins.offset, 2))
        # 加入阻塞
        if type == 0:
            rt_reg.w_busy.append({'add':ins.address,'ins':ins,'tpye':'w'})
            rt_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
            base_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
            # 内存同一时刻只能有一个mem写
            memBusy.append({'add':ins.address,'ins':ins,'type':'LW'})
        # 释放读的寄存器
        elif type == 1:
            # delAdd(memBusy,ind)
            delAdd(base_reg.r_busy,ins)
        # 释放写的寄存器
        elif type == 2:
            delAdd(rt_reg.w_busy,ins)
            delAdd(rt_reg.r_busy,ins)

    # store
    elif ins.opName == "SW" :
        # 要读取的寄存器
        rt_reg = regList[int(ins.rt, 2)]
        base_reg = regList[int(ins.base, 2)]
        # 要存入的内存地址
        ins.mem_value = str(regList[int(ins.base, 2)].value + int(ins.offset, 2))
        if type == 0:
            rt_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
            base_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
            # 内存同一时刻只能有一个mem写
            # memBusy.append(ins.address)
            memBusy.append({'add':ins.address,'ins':ins,'type':'SW'})

        # 释放读的寄存器
        elif type == 1:
            delAdd(rt_reg.r_busy,ins)
            delAdd(base_reg.r_busy,ins)
        # 释放写的寄存器
        elif type == 2:
            pass
            # delAdd(memBusy,ins)

    # 取 rs rt 写rd
    elif ins.opName in ["ADD", "SUB", "MUL", "AND", "OR", "XOR", "NOR", "SLT"] :

        # 要读取的寄存器
        rs_reg = regList[int(ins.rs, 2)]
        rt_reg = regList[int(ins.rt, 2)]
        # 要写入的寄存器编号
        ins.write_reg_num = int(ins.rd, 2)
        rd_reg = regList[int(ins.rd, 2)]

        if type == 0:
            rs_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
            if ins.rs != ins.rt:#有可能 ADD R1 R0 R0
                rt_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
            rd_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
            rd_reg.w_busy.append({'add':ins.address,'ins':ins,'tpye':'w'})
        # 释放读的寄存器
        elif type == 1:
            delAdd(rt_reg.r_busy,ins)
            delAdd(rs_reg.r_busy,ins)
        # 释放写的寄存器
        elif type == 2:
            delAdd(rd_reg.r_busy,ins)
            delAdd(rd_reg.w_busy,ins)

    # 取rt写rd
    elif ins.opName in ["SLL", "SRA", "SRL"]:
        rt_reg = regList[int(ins.rt, 2)]
        ins.write_reg_num = int(ins.rd, 2)
        rd_reg = regList[int(ins.rd, 2)]
        if type == 0:
            rt_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
            rd_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
            rd_reg.w_busy.append({'add':ins.address,'ins':ins,'tpye':'w'})
        # 释放读的寄存器
        elif type == 1:
            delAdd(rt_reg.r_busy,ins)
        # 释放写的寄存器
        elif type == 2:
            delAdd(rd_reg.w_busy,ins)
            delAdd(rd_reg.r_busy,ins)

    # 取rs 写rt或rd
    elif ins.opName in ["ADDI", "ANDI", "ORI", "XORI"]:

        rs_reg = regList[int(ins.rs, 2)]
        rt_reg = regList[int(ins.rt, 2)]
        rd_reg = regList[int(ins.rd, 2)]

        if ins.opName == 'ADDI':
            ins.write_reg_num = int(ins.rt, 2)
            if type == 0:
                rs_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
                rt_reg.w_busy.append({'add':ins.address,'ins':ins,'tpye':'w'})
                rt_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
            elif type == 1:
                delAdd(rs_reg.r_busy,ins)
            elif type == 2:
                delAdd(rt_reg.w_busy,ins)
                delAdd(rt_reg.r_busy,ins)

        else:
            ins.write_reg_num = int(ins.rd, 2)

            if type == 0:
                rs_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
                rd_reg.r_busy.append({'add':ins.address,'ins':ins,'tpye':'r'})
                rd_reg.w_busy.append({'add':ins.address,'ins':ins,'tpye':'w'})

                rs_reg.busy.append({'add': ins.address, 'ins': ins, 'tpye': 'r'})
                rd_reg.busy.append({'add': ins.address, 'ins': ins, 'tpye': 'r'})
                rd_reg.busy.append({'add': ins.address, 'ins': ins, 'tpye': 'w'})
            elif type == 1:
                delAdd(rs_reg.r_busy,ins)
            elif type == 2:
                delAdd(rd_reg.w_busy,ins)
                delAdd(rd_reg.r_busy,ins)


##########################
# issue 从寄存器读取操作数  #
##########################
def issue_exc(ins_type):

    global memBusy
    global Pre_issue
    # 乱序issue  从queue中安先进先出的顺序遍历，如果满足条件就issue
    temp_queue = myQueue()
    temp_ins = 0

    # 从队列中取出指令
    if Pre_issue.emptyl():
        return 0
    issue_success = 0  # issue成功与否

    # 在Pre_issue中顺序找可以issue的指令
    while not Pre_issue.emptyl():
        ins = Pre_issue.getl()
        # 内存指令
        if ins_type == 1 and ins.opName in ["LW","SW"]:
            if checkRegReady(ins) and not issue_success:
                issue_success = 1

        elif ins_type == 0 and not ins.opName in ['LW','SW']:
            if checkRegReady(ins) and not issue_success:
                issue_success = 1

        # 第一次issue成功的存下来
        if issue_success and not temp_ins:
            temp_ins = ins
        # 如果不能issue
        else:
            temp_queue.putl(ins)

    # 将Pre_issue队列遍历一次后，取出了能issue的那一条，把原队列恢复
    Pre_issue.list = temp_queue.list

    if not issue_success:
        # 把不能issue的重新放回Pre_issue
        return 0
    else:
        # print("issue成功", temp_ins.description)

        # 取操作数
        temp_ins.rs_value = regList[int(temp_ins.rs,2)].value
        temp_ins.rt_value = regList[int(temp_ins.rt,2)].value

        # 深拷贝
        temp_ins = copy.deepcopy(temp_ins)
        temp_ins.type = ins_type

        return temp_ins

# 执行运算
def ALU_exc(type):
    # 从pre_ALU取指令和操作数
    # 非 LW SW
    if not type and not Pre_ALU2.emptyl():

        ins = Pre_ALU2.getl()
        # print("ALU阶段",ins.description)
        # 执行操作
        excuteIns(ins)
        # 计算结果写入队列
        # if not Post_ALU2.fulll():
        #     Post_ALU2.putl(ins)
        return ins
    # LW SW
    elif not Pre_ALU1.emptyl():

        ins = Pre_ALU1.getl()
        # print("ALU阶段",ins.description)

        # 执行的 指令 涉及的寄存器  操作数
        excuteIns(ins)
        # 计算结果写入队列
        # if not Post_MEM.fulll():
        #     Post_MEM.putl(ins)
        return ins

# 执行内存操作
def MEM_exc():
    # 从Pre_MEM取指令和操作数
    if Pre_MEM.emptyl():
        return

    ins = Pre_MEM.getl()

    # print("MEM阶段",ins.opName)
    if ins.opName == 'SW':
        memDic[ins.mem_value] = ins.result_value
        # 释放内存锁
        delAdd(memBusy,ins)
    elif ins.opName == 'LW':
        memoryAddress = ins.mem_value
        # memoryAddress = str(regList[int(ins.base, 2)] + int(ins.offset, 2))
        ins.result_value = memDic[memoryAddress]
        # Post_MEM.put(ins)
        delAdd(memBusy,ins)

        return ins
    return 0

# 写入 每次可以写两个，一个来自Post_MEM 一个来自
def WB(type):

    if type and not Post_MEM.emptyl():
        ins = Post_MEM.getl()
        # print("WB阶段 内存",ins.opName)
        scoreBoard(ins,2)
        if ins.opName == 'LW':
            regList[ins.write_reg_num].write(ins.result_value)


    elif not Post_ALU2.emptyl():
        ins = Post_ALU2.getl()
        # print("WB阶段 非内存",ins.opName)

        regList[ins.write_reg_num].write(ins.result_value)
        # 写完解锁寄存器
        scoreBoard(ins,2)


# 执行具体的指令
def excuteIns(ins):

    # insSequenceDic 是地址：指令 键值对

    ins.currentPC = PC_num
    ins.nextPC = PC_num + 4

    if ins.opName == "NOP":
        Operation.ex_NOP(ins)
    elif ins.opName == "ADD":
        Operation.ex_ADD(ins)
    elif ins.opName == "SUB":
        Operation.ex_SUB(ins)
    elif ins.opName == "MUL":
        Operation.ex_MUL(ins)
    elif ins.opName == "AND":
        Operation.ex_AND(ins)
    elif ins.opName == "OR":
        Operation.ex_OR(ins)
    elif ins.opName == "XOR":
        Operation.ex_XOR(ins)
    elif ins.opName == "NOR":
        Operation.ex_NOR(ins)
    elif ins.opName == "SLT":
        Operation.ex_SLT(ins)
    elif ins.opName == "ADDI":
        Operation.ex_ADDI(ins)
    elif ins.opName == "ANDI":
        Operation.ex_ANDI(ins)
    elif ins.opName == "ORI":
        Operation.ex_ORI(ins)
    elif ins.opName == "XORI":
        Operation.ex_XORI(ins)

    elif ins.opName == "SLL":
        Operation.ex_SLL(ins)
    elif ins.opName == "SRL":
        Operation.ex_SRL(ins)
    elif ins.opName == "SRA":
        Operation.ex_SRA(ins)
    elif ins.opName == "SW":
        Operation.ex_SW(ins)
    elif ins.opName == "LW":
        Operation.ex_LW(ins)
    # branch指令
    elif ins.opName == "J":
        Operation.ex_J(ins)
    elif ins.opName == "JR":
        Operation.ex_JR(ins)
    elif ins.opName == "BEQ":
        Operation.ex_BEQ(ins)
    elif ins.opName == "BLTZ":
        Operation.ex_BLTZ(ins)
    elif ins.opName == "BGTZ":
        Operation.ex_BGTZ(ins)
    elif ins.opName == "BREAK":
        Operation.ex_BREAK(ins)


    return ins




# 执行操作的类
class Operation:

    def ex_NOP(ins):
        ins.nextPC += 4

    def ex_ADD(ins):
        # result = ins.rs_value + ins.rt_value
        # reg = regList[ins.write_reg_num]
        # reg.write(result)
        ins.result_value = ins.rs_value + ins.rt_value

    def ex_SUB(ins):
        ins.result_value = ins.rs_value - ins.rt_value

    def ex_MUL(ins):
        ins.result_value = ins.rs_value * ins.rt_value

    def ex_AND(ins):
        ins.result_value = ins.rs_value & ins.rt_value


    def ex_OR(ins):
        ins.result_value = ins.rs_value | ins.rt_value

    def ex_XOR(ins):
        ins.result_value = ins.rs_value ^ ins.rt_value

    def ex_NOR(ins):
        ins.result_value = ~(ins.rs_value | ins.rt_value)


    def ex_SLT(ins):
        ins.result_value = iif(regList[int(ins.rs, 2)].value < regList[int(ins.rt, 2)].value, 1, 0)

    # 写进rt
    def ex_ADDI(ins):
        ins.result_value = ins.rs_value + int(ins.immediate, 2)


    def ex_ANDI(ins):
        ins.result_value = ins.rs_value & int(ins.immediate, 2)

    def ex_ORI(ins):
        ins.result_value = ins.rs_value | int(ins.immediate, 2)

    def ex_XORI(ins):
        ins.result_value = ins.rs_value ^ int(ins.immediate, 2)

    # SLL rd = rt << shiftAmt
    def ex_SLL(ins):
        mask = (2 ** 32) - 1
        # 左移会有溢出
        ins.result_value = (ins.rt_value << int(ins.sa, 2))& mask

        # regList[int(ins.rd, 2)] = (regList[int(ins.rt, 2)] << int(ins.sa, 2)) & mask

    # SRL rd = rt >> sa 算术右移 左边补符号位 >>
    def ex_SRL(ins):
        # regList[int(ins.rd, 2)] = (regList[int(ins.rt, 2)] >> int(ins.sa, 2))
        ins.result_value = ins.rt_value >> int(ins.sa, 2)

    # SRA rd = rt >> sa 逻辑右移 不考虑符号位 左边补0  >>>
    def ex_SRA(ins):
        ins.result_value = ins.rt_value >> int(ins.sa, 2)


    # 部分需要左移两位+"00"
    def ex_J(ins):
        ins.nextPC = int(ins.immediate + "00", 2)
        global PC_num
        PC_num = int(ins.immediate + "00", 2)
        global stalled
        stalled = 0
    def ex_JR(ins):
        ins.nextPC = int(ins.rs + "00", 2)
        global PC_num
        PC_num = int(ins.rs + "00", 2)
        global stalled
        stalled = 0

    # 相等则+offset左移2位跳转
    def ex_BEQ(ins):
        offset = iif(regList[int(ins.rs, 2)].value == regList[int(ins.rt, 2)].value, int(ins.offset + "00", 2), 0)
        ins.nextPC += offset
        global PC_num
        PC_num += offset
        global stalled
        stalled = 0


    # rs<0跳转
    def ex_BLTZ(ins):
        offset = iif(regList[int(ins.rs, 2)].value < 0, int(ins.offset + '00', 2), 0)
        ins.nextPC += offset
        global PC_num
        PC_num += offset
        global stalled
        stalled = 0

    # rs>0跳转
    def ex_BGTZ(ins):
        offset = iif(regList[int(ins.rs, 2)].value > 0, int(ins.offset + '00', 2), 0)
        ins.nextPC += offset
        global PC_num
        PC_num += offset
        global stalled
        stalled = 0

    def ex_BREAK(ins):
        ins.nextPC = -1
        global break_flag
        break_flag = 1

    # SW memory[base+offset] = rt 与LW反向赋值
    def ex_SW(ins):
        memoryAddress = ins.mem_value

        # memoryAddress = str(regList[int(ins.base, 2)] + int(ins.offset, 2))
        # 写入内存
        # memDic[memoryAddress] = ins.rt_value
        ins.result_value = ins.rt_value

    # LW rt = memory[base+offset] base是对应寄存器里面的值  340(R16)
    def ex_LW(ins):
        # memory地址
        memoryAddress = ins.mem_value
        # memoryAddress = str(regList[int(ins.base, 2)] + int(ins.offset, 2))
        ins.result_value = memDic[memoryAddress]



# 三目运算
def iif(condition,true_value,false_value):
    if condition:
        return true_value
    else:
        return false_value

#无符号右移
def unsigned_right_shitf(n,i):
    # 数字小于0，则转为32位无符号uint
    if n<0:
        n = ctypes.c_uint32(n).value

    # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
    if i<0:
        return -(n << abs(i))
    return (n >> i)

# 安全删除register占用队列
def dell(list,i):
    if len(list) >= i+1:
        del list[i]

def delAdd(list,ins):
    for dic in list:
        if dic['add'] == ins.address:
            list.remove(dic)
            break

# 打印队列方法
def printQueue(i):

    global Pre_issue
    global Pre_ALU1
    global Pre_MEM
    global Post_MEM
    global Pre_ALU2
    global Post_ALU2
    global waitingIF
    global executedIF
    Output.slt.pasSim('--------------------\n')
    cycleStr = 'Cycle:'+ str(i) + '\n'+ '\n'
    Output.slt.pasSim(cycleStr)
    Output.slt.pasSim('IF Unit:\n')
    waitingIFStr = ''
    if waitingIF:
        waitingIFStr = '['+waitingIF.description+']'
    executedIFStr = ''
    if executedIF:
        executedIFStr = '['+executedIF.description+']'
    Output.slt.pasSim('\tWaiting Instruction:'+waitingIFStr+'\n')
    Output.slt.pasSim('\tExecuted Instruction:'+executedIFStr+'\n')

    Output.slt.pasSim('Pre-Issue Queue:\n')
    for i in range(0,4):
        insStr = ''
        if len(Pre_issue.list)>=i+1:
            ins = Pre_issue.list[i]
            insStr = '['+ins.description+']'
        Output.slt.pasSim('\tEntry '+str(i)+ ':'+insStr+'\n')

    Output.slt.pasSim('Pre-ALU1 Queue:\n')
    for i in range(0,2):
        insStr = ''
        if len(Pre_ALU1.list)>=i+1:
            ins = Pre_ALU1.list[i]
            insStr = '['+ins.description+']'
        Output.slt.pasSim('\tEntry '+ str(i)+':'+ insStr+'\n')


    insStr = ''
    if len(Pre_MEM.list):
        ins = Pre_MEM.list[0]
        insStr = '['+ ins.description+ ']'
    Output.slt.pasSim('Pre-MEM Queue:'+ insStr+'\n')

    insStr = ''
    if len(Post_MEM.list):
        ins = Post_MEM.list[0]
        insStr = '['+ins.description+']'
    Output.slt.pasSim('Post-MEM Queue:'+ insStr+'\n')

    Output.slt.pasSim('Pre-ALU2 Queue:\n')
    for i in range(0,2):
        insStr = ''
        if len(Pre_ALU2.list)>=i+1:
            ins = Pre_ALU2.list[i]
            insStr = '['+ins.description+']'
        Output.slt.pasSim('\tEntry '+ str(i)+ ':'+ insStr+'\n')

    insStr = ''
    if len(Post_ALU2.list):
        ins = Post_ALU2.list[0]
        insStr = '['+ ins.description +']'
    Output.slt.pasSim('Post_ALU2 Queue:'+insStr+'\n')

    printRegList(regList,memList)



# 按照格式打印regList,memList
def printRegList(regList,memList):
    Output.slt.pasSim('\n\nRegisters\n')
    for i in range(0, len(regList)//8):
        num = i*8
        regNumstr = str(num).zfill(2)
        regNumstr = 'R' + regNumstr + ':'
        numStr = ""
        for j in range(0,8):
            numStr = numStr + '\t' + str(regList[i*8+j].value)
        regNumstr = regNumstr + numStr
        Output.slt.pasSim(regNumstr + '\n')


    Output.slt.pasSim('\nData\n')
    for i in range(0, len(memList)//8):
        strAdd = memList[i*8] + ':'
        strValue = ""
        for j in range(0,8):
            strValue = strValue + '\t' + str(memDic[memList[i*8+j]])
        finalStr = strAdd + strValue
        Output.slt.pasSim(finalStr + '\n')