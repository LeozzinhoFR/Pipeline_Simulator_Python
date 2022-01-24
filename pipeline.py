from ALU import ALU
from binary import Binary
class Pipeline:

    def __init__(self, memory):
        self.__initialize_registers()
        self.__last_cycle = 1
        self.__clock_cycle = 1
        self.__pc = 0
        self.__instruction_memory = memory
        self.__data_memory = {i : 0 for i in range(0,512,4)}

    def __initialize_registers(self):
        self.__registers = {(Binary(decimal = i, bits = 5)).get_code() : 0 for i in range (0,32)}
        #Inicializa registradores de pipeline com valores 0
        self.__bubble_register(0)
        self.__bubble_register(1)
        self.__bubble_register(2)
        self.__bubble_register(3)
        
        self.__forward_unit = {
            'RD' : 0,
            'replace_a' : 0,
            'replace_b' : 0,
            'out' : 0
        }

    def run_step_by_step(self):
        while self.__clock_cycle - self.__last_cycle < 5: #Checa se já se passaram 5 etapas desde o último ciclo com instrução válida
            if self.__pc in self.__instruction_memory:
                self.__last_cycle = self.__clock_cycle
            print('------------Iniciando ciclo '+str(self.__clock_cycle)+'------------\n\n')
            self.__write_back()
            self.__memory_access()
            self.__execution()
            self.__instruction_decode()
            self.__instruction_fetch()
            print('------------Encerrando ciclo '+str(self.__clock_cycle)+'------------\n\n')
            self.__clock_cycle+=1
        print(self.__registers)

    def __write_back(self):
        if self.__mem_wb['wb_control']['RegWrite'] == 0: 
            return #Continuar apenas se RegWrite for 1
        rd = self.__mem_wb['RD'] 
        if self.__mem_wb['wb_control']['MemtoReg'] == 1:
            self.__registers[rd] = self.__mem_wb['wb']     
        else:
            self.__registers[rd] = self.__mem_wb['ALUOut']

    def __bubble_register(self, reg_id):
        if reg_id == 1:
            self.__id_ex = {
                'A' : 0,
                'B' : 0,
                'RT' : 0,
                'RD' : 0,
                'imm' : '0',
                'pc' : 0,
                'wb_control' : {
                    'MemtoReg': 0,
                    'RegWrite': 0
                },
                'mem_control': {
                    'Branch': 0,
                    'branch_aux': 0, #Sinal de controle a mais para facilitar manipulação de tratamento de hazard de controle
                    'MemRead': 0,
                    'MemWrite': 0
                },
                'ex_control':{
                    'RegDst': 0,
                    'ALUSrc': 0,
                    'ALUOp': '000'
                }
            }
        elif reg_id == 2:
            self.__ex_mem = {
                'branch_tg' : 0,
                'zero' : 0,
                'ALUOut' : 0,   
                'B': 0,
                'RD': 0,
                'wb_control' : {
                    'MemtoReg': 0,
                    'RegWrite': 0
                },
                'mem_control': {
                    'Branch': 0,
                    'branch_aux': 0, #Sinal de controle a mais para facilitar manipulação de tratamento de hazard de controle
                    'MemRead': 0,
                    'MemWrite': 0
                }
            }
        elif reg_id == 3:
            self.__mem_wb = {
                'wb' : 0,
                'ALUOut' : 0,
                'RD' : 0,
                'wb_control' : {
                    'MemtoReg': 0,
                    'RegWrite': 0
                }
            }
        elif reg_id == 0:
            self.__if_id = { #Registrador Pipeline para Instruction fetch transição em instruction decode
                'instruction' : Binary(decimal = 0, bits = 32),
                'pc' : 0, #Endereço da próxima instrução
            }

    def __memory_access(self):

        #Passagem de valores de um registrador pipeline para o próximo
        self.__mem_wb['wb_control'] = self.__ex_mem['wb_control'] #Passagem de sinais de controle
        self.__mem_wb['ALUOut'] = self.__ex_mem['ALUOut'] #Passagem de resultado da ALU
        self.__mem_wb['RD'] = self.__ex_mem['RD'] #Passagem de registrador RD

        #Store Word
        if self.__ex_mem['mem_control']['MemWrite'] == 1: 
            self.__data_memory[self.__ex_mem['ALUOut']] = self.__ex_mem['B'] #Armazena na memória o valor armazenado em B
        #Load Word
        if self.__ex_mem['mem_control']['MemRead'] == 1:
            self.__mem_wb['wb'] = self.__data_memory[self.__ex_mem['ALUOut']] #Armazena no MEM_WB o valor da memória
                
    def __execution(self):
        #Passagem de valores de um registrador pipeline para o próximo
        if self.__forward_unit['replace_a'] == 1:
            self.__id_ex['A'] = self.__forward_unit['out']
        elif self.__forward_unit['replace_b'] == 1:
            self.__id_ex['B'] = self.__forward_unit['out']
        self.__ex_mem['mem_control'] = self.__id_ex['mem_control'] #Passagem de sinais de controle
        self.__ex_mem['wb_control'] = self.__id_ex['wb_control']
        self.__ex_mem['B'] = self.__id_ex['B']

        #Definir registrador
        if self.__id_ex['ex_control']['RegDst'] == 1:
            self.__ex_mem['RD'] = self.__id_ex['RD']
        else:
            self.__ex_mem['RD'] = self.__id_ex['RT']

        #Tipo R
        alu = ALU(self.__id_ex['ex_control']['ALUOp'])
        if self.__id_ex['ex_control']['ALUSrc'] == 0:
            zero, out = alu.compute(self.__id_ex['A'], self.__id_ex['B'])
        else:
            zero, out = alu.compute(self.__id_ex['A'], Binary(self.__id_ex['imm']).get_decimal())
        self.__ex_mem['zero'] = zero
        self.__ex_mem['ALUOut'] = out

        

        self.__forward_unit['out'] = out
        self.__forward_unit['RD'] = self.__ex_mem['RD']

        #Branch
        im = Binary(code = self.__id_ex['imm'])
        im.sl_bits(2)
        self.__ex_mem['branch_tg'] = im.get_decimal() + self.__id_ex['pc']
        if self.__ex_mem['mem_control']['Branch'] == 1 and self.__ex_mem['zero'] == 1: 
            if self.__ex_mem['branch_tg'] != self.__id_ex['pc']: #testa se próxima instrução não será o destino do branch
                self.__ex_mem['mem_control']['branch_aux'] = 1       

    def __instruction_fetch(self):
        if self.__pc in self.__instruction_memory:
            self.__if_id['instruction'] = self.__instruction_memory[self.__pc]
        else:
            self.__if_id['instruction'] = Binary(decimal = 0, bits = 32)
        self.__if_id['pc'] = self.__pc

        #Branch
        if self.__ex_mem['mem_control']['branch_aux'] == 1:
            self.__bubble_register(0)
            self.__pc = self.__ex_mem['branch_tg'] #Substitui a próxima instrução com o endereço do branch
        else:
            self.__pc += 4


        print('\nIF_ID\n')
        print(self.__if_id)
        print('\nID_EX\n')
        print(self.__id_ex)
        print('\nEX_MEM\n')
        print(self.__ex_mem)
        print('\nMEM_WB\n')
        print(self.__mem_wb)
        print('\nFORWARD UNIT\n')
        print(self.__forward_unit)

    def __instruction_decode(self):
        if self.__ex_mem['mem_control']['branch_aux'] == 1:
            print('entrou')
            self.__bubble_register(1)
            return
            
        #Passagem normal para o próximo registrador pipeline
        self.__id_ex['pc'] = self.__if_id['pc']
        
        instruction = self.__if_id['instruction'].get_code()
        opcode = instruction[:6]
        rs = instruction[6:11]
        self.__id_ex['A'] = self.__registers[rs]
        rt = instruction[11:16]
        self.__id_ex['RT'] = rt
        self.__id_ex['B'] = self.__registers[rt]
        rd = instruction[16:21]
        self.__id_ex['RD'] = rd
        shamt = instruction[21:26]
        func = instruction[-6:]

        self.__id_ex['imm'] = Binary(code = instruction[16:]).sign_extend(32)
        if opcode == '000000': #INSTRUÇÃO TIPO R

            if rs == self.__forward_unit['RD']:
                self.__forward_unit['replace_a']
            elif rt == self.__forward_unit['RD']:
                self.__forward_unit['replace_b']

            if func == '100000': #ADD
                self.__id_ex['wb_control'] = {
                    'MemtoReg': 0,
                    'RegWrite': 1
                }
                self.__id_ex['mem_control'] = {
                    'Branch': 0,
                    'MemRead': 0,
                    'MemWrite': 0,
                    'branch_aux': 0
                }
                self.__id_ex['ex_control'] = {
                    'RegDst': 1,
                    'ALUSrc': 0,
                    'ALUOp': '010'
                }
            else:
                #FAILSAFE POR ENQUANTO
                self.__id_ex['wb_control'] = {
                    'MemtoReg': 0,
                    'RegWrite': 0
                }
                self.__id_ex['mem_control'] = {
                    'Branch': 0,
                    'MemRead': 0,
                    'MemWrite': 0,
                    'branch_aux': 0
                }
                self.__id_ex['ex_control'] = {
                    'RegDst': 0,
                    'ALUSrc': 0,
                    'ALUOp': '000'
                }
        elif opcode == '001000': #addi

            if rt == self.__forward_unit['RD']:
                self.__forward_unit['replace_a'] = 1

            self.__id_ex['wb_control'] = {
                'MemtoReg': 0,
                'RegWrite': 1
            }
            self.__id_ex['mem_control'] = {
                'Branch': 0,
                'MemRead': 0,
                'MemWrite': 0,
                'branch_aux': 0
            }
            self.__id_ex['ex_control'] = {
                'RegDst': 0,
                'ALUSrc': 1,
                'ALUOp': '010'
            }
        elif opcode == '000100': #BEQ
            self.__id_ex['wb_control'] = {
                'MemtoReg': 0,
                'RegWrite': 0
            }
            self.__id_ex['mem_control'] = {
                'Branch': 1,
                'MemRead': 0,
                'MemWrite': 0,
                'branch_aux': 0
            }
            self.__id_ex['ex_control'] = {
                'RegDst': 0,
                'ALUSrc': 0,
                'ALUOp': '010'
            }



