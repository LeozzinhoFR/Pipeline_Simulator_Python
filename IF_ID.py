from sympy import Q
from binary import Binary
class IF_ID:
    def __init__(self):
        self.empty() #Cria o registrador com valores e sinais de controle vazios

    def empty(self): 
        self.instruction = Binary(decimal = 0, bits = 32) 
        self.pc = 0

    def send_info(self, pc, instruction): #Dados do parâmetros enviados pelo pipeline são registrados
        self.instruction = instruction
        self.pc = pc