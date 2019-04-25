import MIPSsim
import Output


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

