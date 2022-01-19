from ALU import ALU
class Pipeline:


    def __init__(self, memory):
        self.__initialize_registers()
        self.__last_cycle = 1
        self.__clock_cycle = 1
        self.__pc = 0
        self.__instruction_memory = memory
        self.__data_memory = {i : 0 for i in range(0,512,4)}


    def __initialize_registers(self):
        self.__registers = {self.__stringify_number(i, 5) : 1 for i in range (0,32)}

        self.__if_id = { #Registrador Pipeline para Instruction fetch transição em instruction decode
            'instruction' : 0,
            'pc' : 0, #Endereço da próxima instrução
        }

        self.__id_ex = {
            'A' : 0,
            'B' : 0,
            'RT' : int('0', 2),
            'RD' : int('0', 2),
            'imm' : int('0', 2),
            'pc' : 0,
            'wb_control' : {
                'MemtoReg': 0,
                'RegWrite': 0
            },
            'mem_control': {
                'Branch': 0,
                'MemRead': 0,
                'MemWrite': 0
            },
            'ex_control':{
                'RegDst': 0,
                'ALUSrc': 0,
                'ALUOp': '000'
            }
        }

        self.__ex_mem = {
            'branch_tg' : int('0', 2),
            'zero' : 0,
            'ALUOut' : 0,   
            'B': 0,
            'RD': int('0', 2),
            'wb_control' : {
                'MemtoReg': 0,
                'RegWrite': 0
            },
            'mem_control': {
                'Branch': 0,
                'MemRead': 0,
                'MemWrite': 0
            }
        }

        self.__mem_wb = {
            'wb' : 0,
            'ALUOut' : 0,
            'RD' : int('0', 2),
            'wb_control' : {
                'MemtoReg': 0,
                'RegWrite': 0
            }
        }


    def __stringify_number(self, number, char_limit):
        return bin(number)[2:].zfill(char_limit) #Converter número para binário e preencher todos os 32 bits com ele


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
        self.__ex_mem['mem_control'] = self.__id_ex['mem_control'] #Passagem de sinais de controle
        self.__ex_mem['wb_control'] = self.__id_ex['wb_control']
        self.__ex_mem['B'] = self.__id_ex['B']

        #Definir registrador
        if self.__id_ex['ex_control']['RegDst'] == 1:
            self.__ex_mem['RD'] = self.__id_ex['RD']
        else:
            self.__ex_mem['RD'] = self.__id_ex['RT']

        #Tipo R
        if self.__id_ex['ex_control']['ALUSrc'] == 0:
            alu = ALU(self.__id_ex['ex_control']['ALUOp'])
            zero, out = alu.compute(self.__id_ex['A'], self.__id_ex['B'])
            self.__ex_mem['zero'] = zero
            self.__ex_mem['ALUOut'] = out
        

    def __instruction_fetch(self):
        if self.__pc in self.__instruction_memory:
            self.__if_id['instruction'] = self.__instruction_memory[self.__pc]
        else:
            self.__if_id['instruction'] = 0
        self.__if_id['pc'] = self.__pc

        #Branch
        if self.__ex_mem['mem_control']['Branch'] == 1 and self.__mem_wb['mem_control']['zero'] == 1:
            self.__pc = self.__mem_wb['branch_tg'] #Substitui a próxima instrução com o endereço do branch
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


    def __instruction_decode(self):
        #Passagem normal para o próximo registrador pipeline
        self.__id_ex['pc'] = self.__if_id['pc']
        
        instruction = self.__stringify_number(self.__if_id['instruction'], 32)
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
        if opcode == '000000': #INSTRUÇÃO TIPO R
            if func == '100000': #ADD
                self.__id_ex['wb_control'] = {
                    'MemtoReg': 0,
                    'RegWrite': 1
                }
                self.__id_ex['mem_control'] = {
                    'Branch': 0,
                    'MemRead': 0,
                    'MemWrite': 0
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
                    'MemWrite': 0
                }
                self.__id_ex['ex_control'] = {
                    'RegDst': 0,
                    'ALUSrc': 0,
                    'ALUOp': '000'
                }

