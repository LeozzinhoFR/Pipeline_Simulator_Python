class Pipeline:


    def __init__(self, memory):
        self.__initialize_registers()
        self.__clock_cycle = 1
        self.__pc = 0
        self.__instruction_memory = memory

    def __initialize_registers(self):
        self.__if_id = { #Registrador Pipeline para Instruction fetch transição em instruction decode
            'instruction' : int('0', 2),
            'pc' : 0 #Endereço da próxima instrução
        }

        self.__id_ex = {
            'A' : 0,
            'B' : 0,
            'RT' : int('0', 2),
            'RD' : int('0', 2),
            'imm' : int('0', 2),
            'RS' : int('0', 2),
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

    def __stringify_number(self, number):
        return bin(number)[2:].zfill(32) #Converter número para binário e preencher todos os 32 bits com ele

    def run_step_by_step(self):
        self.__write_back()
        self.__memory_access()
        self.__execution()
        self.__instruction_decode()
        self.__instruction_fetch()

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
        self.__mem_wb['wb_control'] = self.__ex_mem['wb_control'] 
        self.__mem_wb['ALUOut'] = self.__ex_mem['ALUOut']
        self.__mem_wb['RD'] = self.__ex_mem['RD']
        
        #Branch
        if self.__mem_wb['mem_control']['Branch'] == 1 and self.__mem_wb['mem_control']['zero'] == 1:
            self.__pc = self.__mem_wb['branch_tg']

    def __instruction_fetch(self):
        self.__if_id['instruction'] = self.__instruction_memory[self.__pc]
        self.__if_id['pc'] = self.__pc
        if self.__control_signals['PCSrc'] == 0:
            self.__pc += 4
        else:
            #TO DO implementar captura de branch
            return

    def __instruction_decode(self):
        instruction = self.__stringify_number(self.__if_id['instruction'])
        opcode = instruction[:6]
        if opcode == '000000': #INSTRUÇÃO TIPO R
            rs = instruction[6:11]
            rt = instruction[11:16]
            rd = instruction[16:21]
            shamt = instruction[21:26]
            func = instruction[-6:]
            if func == '100000': #ADD
                self.__control_signals['ALUOp'] = '010'

