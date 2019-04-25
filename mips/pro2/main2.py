import MIPSsim
import Output
from pro2 import MIPSsim2

if __name__ == '__main__':

    MIPSsim2.initData()
    MIPSsim2.disassemble('new.txt')
    MIPSsim2.excuteInsSequential(256)
    Output.slt.writeSimulation('simulation.txt')
    Output.slt.writeDisassembly('disassembly.txt')