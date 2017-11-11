import MIPSsim
import Output
if __name__ == '__main__':

    MIPSsim.disassemble('sample.txt')
    MIPSsim.excuteInsSequential(256)
    Output.slt.writeSimulation('simulation.txt')
    Output.slt.writeDisassembly('disassembly.txt')