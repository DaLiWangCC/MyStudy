from enum import Enum
import Operation
import Instruction
import Output

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
# 初始化寄存器list
regList = [0 for i in range(32)]
# memList memDic
memList = []
memDic = {}
cycle = 1

# 反汇编
def disassemble(fileName):

    f = open(fileName, "r")
    line = f.readline()
    address = 256
    while line:
        opetation = line[0:6]
        if opetation not in ins2BinaryDic.keys():
            # 非指令 即为内存
            # 补码
            if line[0]=='1':
                memoryValue = int(line, 2)- (1<<32)
            else:
                memoryValue = int(str(line), 2)

            memList.append(str(address))
            memDic[str(address)] = memoryValue
            line = f.readline()
            address += 4
            continue

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
        ins.currentPC = address
        # 指令和指令地址存入字典
        insSequenceDic[str(address)] = ins
        address += 4

        line = f.readline()

# 顺序执行指令
def excuteInsSequential(address):
    while address != -1:
        address = excuteIns(address)

# 执行具体的指令
def excuteIns(address):
    # for ins in insList:
        ins = insSequenceDic[str(address)]
        global cycle
        ins.cycle = cycle
        ins.printInstruction()
        ins.currentPC = address
        ins.nextPC = address + 4

        if ins.opName == "NOP":
            Operation.ex_NOP(ins,regList)
        elif ins.opName == "ADD":
            Operation.ex_ADD(ins,regList)
        elif ins.opName == "SUB":
            Operation.ex_SUB(ins, regList)
        elif ins.opName == "MUL":
            Operation.ex_MUL(ins, regList)
        elif ins.opName == "AND":
            Operation.ex_AND(ins, regList)
        elif ins.opName == "OR":
            Operation.ex_OR(ins, regList)
        elif ins.opName == "XOR":
            Operation.ex_XOR(ins, regList)
        elif ins.opName == "NOR":
            Operation.ex_NOR(ins, regList)
        elif ins.opName == "SLT":
            Operation.ex_SLT(ins, regList)
        elif ins.opName == "ADDI":
            Operation.ex_ADDI(ins, regList)
        elif ins.opName == "ANDI":
            Operation.ex_ANDI(ins, regList)
        elif ins.opName == "ORI":
            Operation.ex_ORI(ins, regList)
        elif ins.opName == "XORI":
            Operation.ex_XORI(ins, regList)

        elif ins.opName == "J":
            Operation.ex_J(ins, regList)
        elif ins.opName == "JR":
            Operation.ex_JR(ins, regList)
        elif ins.opName == "BEQ":
            Operation.ex_BEQ(ins, regList)
        elif ins.opName == "BLTZ":
            Operation.ex_BLTZ(ins, regList)
        elif ins.opName == "BGTZ":
            Operation.ex_BGTZ(ins, regList)
        elif ins.opName == "BREAK":
            Operation.ex_BREAK(ins, regList)
        elif ins.opName == "SW":
            Operation.ex_SW(ins, regList, memDic)
        elif ins.opName == "LW":
            Operation.ex_LW(ins, regList, memDic)
        elif ins.opName == "SLL":
            Operation.ex_SLL(ins, regList)
        elif ins.opName == "SRL":
            Operation.ex_SRL(ins, regList)
        elif ins.opName == "SRA":
            Operation.ex_SRA(ins, regList)

        # Output.slt.pas()('nextPC',ins.nextPC)
        cycle += 1
        printRegList(regList,memList)
        return ins.nextPC


# 打印regList,memList
def printRegList(regList,memList):
    Output.slt.pasSim('\n\nRegisters\n')
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

    Output.slt.pasSim(str1+'\n')
    Output.slt.pasSim(str2+'\n')
    Output.slt.pasSim(str3+'\n')
    Output.slt.pasSim(str4+'\n')
    Output.slt.pasSim('\n')

    Output.slt.pasSim('Data\n')
    str1 = '340:'
    for i in range(8):
        str1 = str1 + '\t' + str(memDic[memList[i]])

    str2 = '372:'
    for i in range(8):
        str2 = str2 + '\t' + str(memDic[memList[i + 8]])
    str3 = '404:'
    for i in range(8):
        str3 = str3 + '\t' + str(memDic[memList[i + 16]])

    Output.slt.pasSim(str1+'\n')
    Output.slt.pasSim(str2+'\n')
    Output.slt.pasSim(str3+'\n')




