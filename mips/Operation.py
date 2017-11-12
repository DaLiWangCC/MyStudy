import Instruction

def ex_NOP(ins,regList):
    ins.nextPC += 4
def ex_ADD(ins,regList):
    regList[int(ins.rd,2)] = regList[int(ins.rs,2)]+regList[int(ins.rt,2)]
def ex_SUB(ins,regList):
    regList[int(ins.rd,2)] = regList[int(ins.rs,2)]-regList[int(ins.rt,2)]
def ex_MUL(ins,regList):
    regList[int(ins.rd,2)] = regList[int(ins.rs,2)]*regList[int(ins.rt,2)]
def ex_AND(ins,regList):
    regList[int(ins.rd,2)] = regList[int(ins.rs,2)] & regList[int(ins.rt,2)]
def ex_OR(ins,regList):
    regList[int(ins.rd,2)] = regList[int(ins.rs,2)] | regList[int(ins.rt,2)]
def ex_XOR(ins,regList):
    regList[int(ins.rd,2)] = regList[int(ins.rs,2)] ^ regList[int(ins.rt,2)]
def ex_NOR(ins,regList):
    regList[int(ins.rd,2)] =  ~(regList[int(ins.rs,2)] | regList[int(ins.rt,2)])
def ex_SLT(ins,regList):
    regList[int(ins.rd,2)] = iif(regList[int(ins.rs,2)] < regList[int(ins.rt,2)],1,0)
def ex_ADDI(ins,regList):
    regList[int(ins.rt,2)] =  regList[int(ins.rs,2)] + int(ins.immediate,2)
def ex_ANDI(ins,regList):
    regList[int(ins.rd,2)] =  regList[int(ins.rs,2)] & int(ins.immediate,2)
def ex_ORI(ins,regList):
    regList[int(ins.rd,2)] =  regList[int(ins.rs,2)] | int(ins.immediate,2)
def ex_XORI(ins,regList):
    regList[int(ins.rd,2)] =  regList[int(ins.rs,2)] ^ int(ins.immediate,2)

# 部分需要左移两位+"00"
def ex_J(ins,regList):
    ins.nextPC = int(ins.immediate+"00",2)
def ex_JR(ins,regList):
    ins.nextPC = int(ins.rs+"00",2)
# 相等则+offset左移2位跳转
def ex_BEQ(ins,regList):
    offset = iif(regList[int(ins.rs,2)] == regList[int(ins.rt,2)],int(ins.offset+"00",2),0)
    ins.nextPC += offset
# rs<0跳转
def ex_BLTZ(ins,regList):
    offset = iif(regList[int(ins.rs, 2)] < 0, int(ins.offset+'00',2),0)
    ins.nextPC += offset
# rs>0跳转
def ex_BGTZ(ins,regList):
    offset = iif(regList[int(ins.rs, 2)] > 0, int(ins.offset+'00',2),0)
    ins.nextPC += offset
def ex_BREAK(ins,regList):
    ins.nextPC = -1
# SW memory[base+offset] = rt 与LW反向赋值
def ex_SW(ins,regList,memDic):
    memoryAddress = str(regList[int(ins.base, 2)] + int(ins.offset, 2))
    num = regList[int(ins.rt, 2)]
    memDic[memoryAddress] = regList[int(ins.rt, 2)]
# LW rt = memory[base+offset] base是对应寄存器里面的值  340(R16)
def ex_LW(ins,regList,memDic):
    # memory地址
    memoryAddress = str(regList[int(ins.base, 2)] + int(ins.offset, 2))
    regList[int(ins.rt, 2)] = memDic[memoryAddress]
# SLL rd = rt << shiftAmt
def ex_SLL(ins,regList):
    mask = (2**32) - 1
    # 左移会有溢出
    regList[int(ins.rd, 2)] = (regList[int(ins.rt, 2)] << int(ins.sa, 2)) & mask

# SRL rd = rt >> sa
def ex_SRL(ins,regList):
    regList[int(ins.rd, 2)] = (regList[int(ins.rt, 2)] >> int(ins.sa, 2))

# SRA rd = rt >> sa
def ex_SRA(ins,regList):
    regList[int(ins.rd, 2)] = (regList[int(ins.rt, 2)] >> int(ins.sa, 2))




# 三目运算
def iif(condition,true_value,false_value):
    if condition:
        return true_value
    else:
        return false_value