from ALU import ALU
from MEM_WB import MEM_WB
from EX_MEM import EX_MEM
from ID_EX import ID_EX
from IF_ID import IF_ID
from binary import Binary
class Pipeline:

    def __init__(self, memory):
        self.__initialize_registers()
        self.__last_cycle = 1
        self.clock_cycle = 1
        self.pc = 0
        self.instruction_memory = memory
        self.data_memory = {i : 0 for i in range(0,512,4)}

    def __initialize_registers(self):
        #Banco de Registradores
        self.registers = {(Binary(decimal = i, bits = 5)).get_code() : 0 for i in range (0,32)}

        #Registradores Pipeline
        if_id = IF_ID()
        id_ex = ID_EX(if_id)
        ex_mem = EX_MEM(id_ex)
        mem_wb = MEM_WB(ex_mem)

        #Unidade auxiliar para lidar com hazard de dados
        self.forward_unit = {
            'RD' : 0,
            'replace_a' : 0,
            'replace_b' : 0,
            'out' : 0
        }

    def run(self):
        f = open('output.txt', 'w')
        while self.clock_cycle - self.__last_cycle < 5: #Checa se já se passaram 5 etapas desde o último ciclo com instrução válida
            
            #WRITE-BACK
            if self.mem_wb.wb_control['RegWrite'] == 1: 
                rd = self.mem_wb.RD 
                if self.mem_wb.wb_control['MemtoReg'] == 1:
                    self.registers[rd] = self.mem_wb.wb     
                else:
                    self.registers[rd] = self.mem_wb.ALUOut

            #MEMORY ACCESS
            self.mem_wb.send_info(self.data_memory) #Envia informações para o registrador mem_wb

            #Store Word
            if self.ex_mem.mem_control['MemWrite'] == 1: 
                self.data_memory[self.ex_mem.ALUOut] = self.ex_mem.B #Armazena na memória o valor armazenado em B

            #EXECUTION
            self.ex_mem.send_info(self.forward_unit['replace_a'], self.forward_unit['replace_b'], self.forward_unit['out']) #Envia informações para o registrador mem_wb

            self.forward_unit['out'] = self.ex_mem.ALUOut
            self.forward_unit['RD'] = self.ex_mem.RD

            #DECODE
            rs, rt, i_type = self.id_ex.send_info(self.registers) 
            if i_type == 'r':
                if rt == self.forward_unit['RD']:
                    self.forward_unit['replace_a'] = 1
            elif i_type == 'i':
                if rs == self.forward_unit['RD']:
                    self.forward_unit['replace_a']
                elif rt == self.forward_unit['RD']:
                    self.forward_unit['replace_b']
           

            #FETCH
            if self.pc in self.instruction_memory:
                self.__last_cycle = self.clock_cycle
                self.if_id.send_info(self.pc, self.instruction_memory[self.pc])
            else:
                self.if_id.send_info(self.pc, Binary(decimal = 0, bits = 32))
            
            #Branch
            if self.ex_mem.mem_control['branch_aux'] == 1:
                self.if_id.empty()
                self.pc = self.ex_mem['branch_tg'] #Substitui a próxima instrução com o endereço do branch
            else:
                self.pc += 4

            self.print_pipeline_registers(f)

            self.clock_cycle+=1

        f.write('\n\n--------------\n\n')
        f.write(str(self.registers))

def print_pipeline_registers(self, f): #Mostra os pipelines de registrador em cada ciclo de clock em um arquivo de output para testagem
    f.write('\n\n\nAo fim do ciclo '+str(self.clock_cycle)) 
    f.write(':\n\n')
    f.write('----IF_ID----\n')
    f.write('\n')
    f.write('instruction: '+self.if_id.instruction.get_code())
    f.write('\n')
    f.write('pc: '+str(self.if_id.pc))
    f.write('\n\n')
    f.write('----ID_EX----\n')
    f.write('\n')
    f.write('A: '+str(self.id_ex.A))
    f.write('\n')
    f.write('B: '+str(self.id_ex.B))
    f.write('\n')
    f.write('RT: '+str(self.id_ex.RT))
    f.write('\n')
    f.write('RD: '+str(self.id_ex.RD))
    f.write('\n')
    f.write('imm: '+self.id_ex.imm)
    f.write('\n')
    f.write('pc: '+str(self.id_ex.pc))
    f.write('\n')
    f.write('wb_control: ')
    f.write(str(self.id_ex.wb_control))
    f.write('\n')
    f.write('mem_control: ')
    f.write(str(self.id_ex.mem_control))
    f.write('\n')
    f.write('ex_control: ')
    f.write(str(self.id_ex.ex_control))
    f.write('\n\n')
    f.write('----EX_MEM----\n')
    f.write('\n')
    f.write('branch_tg: '+str(self.ex_mem.branch_tg))
    f.write('\n')
    f.write('zero: '+str(self.ex_mem.zero))
    f.write('\n')
    f.write('ALUOut: '+str(self.ex_mem.ALUOut))
    f.write('\n')
    f.write('B: '+str(self.ex_mem.B))
    f.write('\n')
    f.write('RD: '+str(self.ex_mem.RD))
    f.write('\n')
    f.write('wb_control: ')
    f.write(str(self.ex_mem.wb_control))
    f.write('\n')
    f.write('mem_control: ')
    f.write(str(self.ex_mem.mem_control))
    f.write('\n\n')
    f.write('----MEM_WB----\n')
    f.write('\n')
    f.write('wb: '+str(self.mem_wb))
    f.write('\n')     
    f.write('ALUOut: '+str(self.mem_wb.ALUOut))
    f.write('\n')
    f.write('RD: '+str(self.mem_wb.RD))
    f.write('\n')
    f.write('wb_control: ')
    f.write(str(self.mem_wb.wb_control))

