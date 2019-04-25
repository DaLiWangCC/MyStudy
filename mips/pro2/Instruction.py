import MIPSsim
import Output

# tag = 0 打印反汇编  tag = 1 打印执行过程

# 指令类
class Instruction:
    printDisOrSimtag = 0

    def __init__(self):

        # 指令存放地址
        self.address = 0
        # 操作名称
        self.opName = ''
        # 操作码
        self.op = ''
        # 标识
        self.identification = ''
        # 目标
        self.target = ''
        # 偏移量
        self.offset = ""
        # 从寄存器取
        self.base = ""
        # 移位
        self.sa = ""
        # 源寄存器
        self.rs = ""
        self.rs_value = 0
        # 目标寄存器
        self.rt = ""
        self.rt_value = 0
        # 寄存器
        self.rd = ""
        # 最终写入寄存器的编号
        self.write_reg_num = 0
        # 最终要写入的值
        self.result_value = 0
        # 内存操作地址
        self.mem_value = 0
        # 立即数
        self.immediate = ""
        # 移位数
        self.shiftAmt = ""
        # offset
        self.offset = ""
        #剩余
        self.lastStr = ''
        # 打印类型
        self.printTag = 0
        # 当前指令地址
        self.currentPC = 0
        # 下条指令地址
        self.nextPC = 0
        # 指令计数
        self.insNum = 0
        self.cycle = 0
        # 01指令字符串
        self.line = ''
        # index
        self.instr_index = ''
        # 指令占据的寄存器
        self.using_reg = []
        # 是否是内存指令
        self.type = 0

        # 指令的描述
        self.description = ''
    # 打印本条指令 1:op rs rt rd   2:op rs rt imm   3:op index
    # tag = 0 打印反汇编  tag = 1 打印执行过程
    def printInstruction(self,tag):
        global printDisOrSimtag
        printDisOrSimtag = tag
        if self.printTag == "OpRsRtRd":
            return print_ins_OpRsRtRd(self)
        elif self.printTag == "OpRsRtImm":
            return print_ins_OpRsRtImm(self)
        elif self.printTag == "OpRsRtOffsetLS":
            return print_ins_OpRsRtOffsetLS(self)
        elif self.printTag == "OpIndex":
            return print_ins_OpIndex(self)
        elif self.printTag == "OpRsOffset":
            return print_ins_OpRsOffset(self)
        elif self.printTag == "OpRsMem":
            return print_ins_OpRsMem(self)
        elif self.printTag == "OpRs":
            return print_ins_OpRs(self)
        elif self.printTag == "OpRdRtSa":
            return print_ins_OpRdRtSa(self)
        elif self.printTag == "Op":
            return print_ins_Op(self)
        Output.slt.pasDis('\n')


# 拼接寄存器名称
def appendRegName(regStr):
    return "R" + str(int(regStr, 2))
def print_ins_Op(ins):
    ins.description = ins.opName
    insStr = str(ins.currentPC) + ' ' + ins.opName
    if printDisOrSimtag:
        return ins.line+'\t'+insStr
    else:
        return ('Cycle:' + str(ins.cycle) + ' ' + insStr)
def print_ins_OpRs(ins):
    rs = appendRegName(ins.rs)
    rt = appendRegName(ins.rt)
    rd = appendRegName(ins.rd)
    ins.description = ins.opName + " " + rs
    insStr = str(ins.currentPC) + ' ' + ins.opName + " " + rs
    if printDisOrSimtag:
        return (ins.line+'\t'+insStr)
    else:
        return ('Cycle:' + str(ins.cycle) + ' ' + insStr)
# 打印指令 op rs rt rd 类型
def print_ins_OpRsRtRd(ins):
    rs = appendRegName(ins.rs)
    rt = appendRegName(ins.rt)
    rd = appendRegName(ins.rd)
    ins.description = ins.opName+" "+rd+"," + rs + "," +rt
    insStr = str(ins.currentPC) + ' ' + ins.opName+" "+rd+"," + rs + "," +rt
    if printDisOrSimtag:
        return (ins.line+'\t'+insStr)
    else:
        return ('Cycle:' + str(ins.cycle) + ' '+ insStr)

# 打印指令 op rs rt immediate 类型
def print_ins_OpRsRtImm(ins):
    rs = appendRegName(ins.rs)
    rt = appendRegName(ins.rt)
    immediate = "#"+str(int(ins.immediate, 2))
    ins.description = ins.opName + " " + rt +"," + rs + "," +immediate
    insStr = str(ins.currentPC) + ' ' + ins.opName + " " + rt +"," + rs + "," +immediate
    if printDisOrSimtag:
        return (ins.line+'\t'+insStr)
    else:
        return ('Cycle:' + str(ins.cycle) + ' ' + insStr)

# 打印指令 op rs rt immediate左移2位 类型
def print_ins_OpRsRtOffsetLS(ins):
    rs = appendRegName(ins.rs)
    rt = appendRegName(ins.rt)
    offset = "#"+str(int(ins.offset+'00', 2))
    ins.description = ins.opName + " " + rs +',' + rt + ',' +offset
    insStr = str(ins.currentPC) + ' ' + ins.opName + " " + rs +',' + rt + ',' +offset
    if printDisOrSimtag:
        return (ins.line+'\t'+insStr)
    else:
        return ('Cycle:' + str(ins.cycle) + ' ' +insStr)

# 打印指令 op rs rt sa 类型
def print_ins_OpRdRtSa(ins):
    rd = appendRegName(ins.rd)
    rt = appendRegName(ins.rt)
    sa = '#'+str(int(ins.sa,2))
    ins.description = ins.opName + " " + rd +"," + rt + "," +sa
    insStr = str(ins.currentPC) + ' ' + ins.opName + " " + rd +"," + rt + "," +sa
    if printDisOrSimtag:
        return (ins.line+'\t'+insStr)
    else:
        return ('Cycle:' + str(ins.cycle) + ' ' + insStr)

# 打印指令 op rs  offset 类型
def print_ins_OpRsOffset(ins):
    rs = appendRegName(ins.rs)
    offset = "#"+str(int(ins.offset+'00', 2))
    ins.description = ins.opName+" "+rs+ "," +offset
    insStr = str(ins.currentPC) + ' ' + ins.opName+" "+rs+ "," +offset
    if printDisOrSimtag:
        return (ins.line+'\t'+insStr)
    else:
        return ('Cycle:' + str(ins.cycle) + ' ' + insStr)

# 打印指令 op rs  offset(Rbase) 类型  rt ← memory[base+offset]
def print_ins_OpRsMem(ins):
    rt = appendRegName(ins.rt)
    offset = str(int(ins.offset, 2))
    Rbase = '(R'+str(int(ins.base,2))+')'
    ins.description = ins.opName+" "+rt+ "," +offset+Rbase
    insStr = str(ins.currentPC) + ' ' + ins.opName+" "+rt+ "," +offset+Rbase
    if printDisOrSimtag:
        return (ins.line+'\t'+insStr)
    else:
        return ('Cycle:' + str(ins.cycle) + ' ' + insStr)

# 打印指令 op index 类型
def print_ins_OpIndex(ins):
    x = eval("0b" + ins.instr_index+'00')
    instr_index = "#"+str(x)
    ins.description = ins.opName + " " + instr_index
    insStr = str(ins.currentPC) + ' ' + ins.opName + " " + instr_index
    if printDisOrSimtag:
        return (ins.line+'\t'+insStr)
    else:
        return ('Cycle:' + str(ins.cycle) + ' ' + insStr)

