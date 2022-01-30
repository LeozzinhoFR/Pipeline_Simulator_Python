from ALU import ALU
from MEM_WB import MEM_WB
from EX_MEM import EX_MEM
from ID_EX import ID_EX
from IF_ID import IF_ID
from binary import Binary
import time
class Pipeline:

    def __init__(self, memory):
        self.__initialize_registers()
        self.__last_cycle = 1
        self.clock_cycle = 1
        self.pc = 0
        self.instruction_memory = memory
        self.data_memory = {i : 0 for i in range(0,512,4)}

        #variáveis para armazenar a instrução sendo executada em cada estágio do pipeline
        self.fetch = '00000000000000000000000000000000'
        self.decode = self.fetch
        self.execution = self.decode
        self.memory_access = self.execution
        self.writeback = self.memory_access

    def __initialize_registers(self):
        #Banco de Registradores
        self.registers = {(Binary(decimal = i, bits = 5)).get_code() : 0 for i in range (0,32)}

        #Registradores Pipeline
        self.if_id = IF_ID()
        self.id_ex = ID_EX(self.if_id)
        self.ex_mem = EX_MEM(self.id_ex)
        self.mem_wb = MEM_WB(self.ex_mem)

        #Unidades auxiliar para lidar com hazard de dados
        self.forward_unit = {
            'RD' : 0,
            'replace_a' : 0,
            'replace_b' : 0,
            'out' : 0,
            'mem_out' : 0,
            'FWDSrc' : 0 #Se for 1, o out vem da leitura da memória, senão vem do ALUOut
        }
        self.stall_unit = {
            'delay' : 0
        }

    def run(self, step_by_step):
        stall_count = 0
        f = open('pipeline_registers.txt', 'w')
        data_output = open('data_memory.txt', 'w')
        while self.clock_cycle - self.__last_cycle < 5 + stall_count: #Checa se já se passaram 5 etapas desde o último ciclo com instrução válida
            #WRITE-BACK
            self.writeback = self.memory_access
            if self.mem_wb.wb_control['RegWrite'] == 1: 
                rd = self.mem_wb.RD 
                mem_to_reg = self.mem_wb.wb_control['MemtoReg']
                if mem_to_reg == 1:
                    self.registers[rd] = self.mem_wb.wb     
                elif mem_to_reg == 0:
                    self.registers[rd] = self.mem_wb.ALUOut
                else: #Caso de JAL
                    self.registers[rd] = self.mem_wb.pc + 4

            #MEMORY ACCESS
            self.memory_access = self.execution
            self.mem_wb.send_info(self.data_memory) #Envia informações para o registrador mem_wb
            if self.mem_wb.wb_control['MemtoReg'] == 1: #Se a instrução for de load atualizar o valor no forwarding
                self.forward_unit['mem_out'] = self.mem_wb.wb
            


            #Store Word
            if self.ex_mem.mem_control['MemWrite'] == 1: 
                self.data_memory[self.ex_mem.ALUOut] = self.ex_mem.B #Armazena na memória o valor armazenado em B
            

            #EXECUTION

            if self.stall_unit['delay'] == 0: #Execução não ocorre em caso de stall
                self.execution = self.decode
                if self.forward_unit['FWDSrc'] == 1:
                    self.ex_mem.send_info(self.forward_unit['replace_a'], self.forward_unit['replace_b'], self.forward_unit['mem_out']) #Envia informações para o registrador mem_wb    
                    self.forward_unit['FWDSrc'] = 0
                else:
                    self.ex_mem.send_info(self.forward_unit['replace_a'], self.forward_unit['replace_b'], self.forward_unit['out']) #Envia informações para o registrador mem_wb    
            else:
                self.execution = '00000000000000000000000000000000'
                self.ex_mem.empty()



            #STALL MANAGEMENT
            is_lw = self.ex_mem.wb_control['MemtoReg'] == 1 #Checar se a execução era uma lw para administrar stall em caso de data hazard
            self.stall_unit['delay'] = 0 #Por padrão não há delay, apenas em caso de hazard

            #DECODE
            self.decode = self.fetch
            rs, rt, i_type = self.id_ex.send_info(self.registers)

            #Controle de unidade de forwarding
            if self.forward_unit['FWDSrc'] == 0:
                self.forward_unit['mem_out'] = self.mem_wb.wb
                self.forward_unit['RD'] = self.ex_mem.RD
                self.forward_unit['out'] = self.ex_mem.ALUOut 
                self.forward_unit['replace_a'] = 0 #Por padrão o valor de controle aqui é 0
                self.forward_unit['replace_b'] = 0 #Passa a ser 1 conforme for necessário

                if i_type == 'i':
                    if rt == self.forward_unit['RD']:                        
                        if is_lw: 
                            self.stall_unit['delay'] = 1
                            stall_count+=1
                            self.forward_unit['FWDSrc'] = 1
                        self.forward_unit['replace_a'] = 1
                elif i_type == 'r':
                    if rs == self.forward_unit['RD']:
                        if is_lw: 
                            self.stall_unit['delay'] = 1
                            stall_count+=1
                            self.forward_unit['FWDSrc'] = 1
                        self.forward_unit['replace_a'] = 1
                    if rt == self.forward_unit['RD']:
                        if is_lw: 
                            self.stall_unit['delay'] = 1
                            stall_count+=1
                            self.forward_unit['FWDSrc'] = 1
                        self.forward_unit['replace_b'] = 1
            

            #FETCH
            if self.stall_unit['delay'] == 0:
                if self.pc in self.instruction_memory:
                    self.__last_cycle = self.clock_cycle
                    self.if_id.send_info(self.pc, self.instruction_memory[self.pc])
                else:
                    self.if_id.send_info(self.pc, Binary(decimal = 0, bits = 32))
                self.fetch = self.if_id.instruction.get_code()
            else:
                self.id_ex.empty()
                self.fetch = '00000000000000000000000000000000'
                
            #Imprimir informações do ciclo antes de alterar o PC
            print('Ciclo de clock atual: '+str(self.clock_cycle))
            print('PC atual: '+str(self.pc))
            print('Estágio de IF: '+self.fetch)
            print('Estágio de ID: '+self.decode)
            print('Estágio de EX: '+self.execution)
            print('Estágio de MEM: '+self.memory_access)
            print('Estágio de WB: '+self.writeback)
            print('Banco de registradores: ')
            print(self.registers)
            print('\n')
            if step_by_step:
                time.sleep(1.5)
            
            #Branch
            if self.stall_unit['delay'] == 0:
                if self.ex_mem.mem_control['branch_aux'] == 1 or self.ex_mem.mem_control['jr'] == 1:
                    self.if_id.empty()
                    self.id_ex.empty()
                    self.pc = self.ex_mem.branch_tg #Substitui a próxima instrução com o endereço do branch
                else:
                    self.pc += 4
            
            #Jump
            if self.id_ex.mem_control['uncond_jump'] == 1:
                self.if_id.empty()
                target = Binary(code = self.id_ex.jump)
                target.sl_bits(2)
                branch_tg = target.get_decimal()
                self.pc = branch_tg

            self.print_pipeline_registers(f)
            self.clock_cycle+=1

        f.write('\n\n--------------\n\n')
        f.write(str(self.registers))
        f.write('\n\n--------------\n\n')
        f.write(str(self.data_memory))

        #Output de dados
        for i in self.data_memory:
            data_output.write(str(i)+': '+str(self.data_memory[i])+'\n')

    def print_pipeline_registers(self, f): #Mostra os pipelines de registrador em cada ciclo de clock em um arquivo de output para testagem
        f.write('\n\n\n-------------------------Ao fim do ciclo '+str(self.clock_cycle)) 
        f.write(':-------------------------\n\n')
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
        f.write('jump: '+str(self.id_ex.jump))
        f.write('\n')
        f.write('RT: '+str(self.id_ex.RT))
        f.write('\n')
        f.write('RD: '+str(self.id_ex.RD))
        f.write('\n')
        f.write('imm: '+self.id_ex.imm)
        f.write('\n')
        f.write('pc: '+str(self.id_ex.pc))
        f.write('\n')
        f.write('sa: '+str(self.id_ex.sa))
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
        f.write('wb: '+str(self.mem_wb.wb))
        f.write('\n')     
        f.write('ALUOut: '+str(self.mem_wb.ALUOut))
        f.write('\n')
        f.write('RD: '+str(self.mem_wb.RD))
        f.write('\n')
        f.write('wb_control: ')
        f.write(str(self.mem_wb.wb_control))
        f.write('\n\n----FWD_UNIT----\n')
        f.write('\n')
        f.write(str(self.forward_unit))
        f.write('\n\n----STALL_UNIT----\n')
        f.write('\n')
        f.write(str(self.stall_unit))