from binary import Binary

class MEM_WB:
    def __init__(self, prev):
        self.prev = prev #Registrador EX_MEM

        #Registradores
        self.empty() #Cria o registrador com valores e sinais de controle vazios

    def empty(self): 
        self.wb = 0
        self.pc = 0
        self.ALUOut = 0
        self.RD = 0
        self.wb_control = {
            'MemtoReg': 0,
            'RegWrite': 0
        }

    def send_info(self, data_memory):
        self.wb_control = self.prev.wb_control

        self.ALUOut = self.prev.ALUOut
        self.RD = self.prev.RD
        self.pc = self.prev.pc

        #Load Word
        if self.prev.mem_control['MemRead'] == 1:
            self.wb = data_memory[self.prev.ALUOut] #Armazena no MEM_WB o valor da memória. ALUOut deve ser múltiplo de 4
            
