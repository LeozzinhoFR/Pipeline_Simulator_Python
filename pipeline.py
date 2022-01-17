class Pipeline:


    def __init__(self, memory):
        self.__initialize_registers()
        self.control_signals = {
            'RegDst' : 0,
            'RegWrite' : 0,
            'ALUSrc' : 0,
            'PCSrc': 0, #Quando 0: PC+4, Quando 1: Branch
            'MemRead': 0,
            'MemWrite': 0,
            'MemtoReg': 0
        }
        self._clock_cycle = 1
        self._pc = 0
        self._instruction_memory = memory
        print(self._instruction_memory)
        print(bin(self._instruction_memory[0])[2:].zfill(32))
        print(bin(self._instruction_memory[0] << 2)[2:].zfill(32))

    def __initialize_registers(self):
        self.if_id = { #Registrador Pipeline para Instruction fetch transição em instruction decode
            'instruction' : int(0, 2),
            'pc' : 0 #Endereço da próxima instrução
        }

    def __stringify_number(self, number):
        return bin(number)[2:].zfill(32) #Converter número para binário e preencher todos os 32 bits com ele

    def run_step_by_step(self):
        self.__instruction_fetch()
        self.__instruction_decode()
    
    def __instruction_fetch(self):
        self.if_id['instruction'] = self._instruction_memory[self.pc]
        self.if_id['pc'] = self.pc
        if self.control_signals['PCSrc'] == 0:
            self.pc += 4
        else:
            #TO DO implementar captura de branch
            return

    def __instruction_decode(self):
        return
