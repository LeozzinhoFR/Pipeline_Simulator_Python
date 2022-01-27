from binary import Binary
from ALU import ALU

class EX_MEM:
    def __init__(self, prev):
        self.prev = prev #Registrador ID_EX

        #Registradores
        self.empty() #Cria o registrador com valores e sinais de controle vazios

    def empty(self): 
        self.branch_tg = 0
        self.zero = 0
        self.ALUOut = 0   
        self.B = 0
        self.RD = 0
        self.wb_control = {
            'MemtoReg': 0,
            'RegWrite': 0
        }
        self.mem_control = {
            'Branch': 0,
            'branch_aux': 0, #Sinal de controle a mais para facilitar manipulação de tratamento de hazard de controle
            'MemRead': 0,
            'MemWrite': 0
        }
            
    def send_info(self, replace_a, replace_b, out): #Dados do parâmetros do pipeline passado são calculados e passados para um novo
        #Valores passados diretamente de um registrador ao outro
        self.wb_control = self.prev.wb_control
        self.mem_control = self.prev.mem_control
        self.B = self.prev.B

        #Variáveis temporárias para fazer o cálculo na ALU
        A = self.prev.A 
        B = self.prev.B

        #Hazard de dados
        if replace_a == 1:
            A = out
        elif replace_b == 1:
            B = out

        #Definir registrador destino
        if self.prev.ex_control['RegDst'] == 1:
            self.RD = self.prev.RD
        else:
            self.RD = self.prev.RT

        #Cálculos da ALU
        alu = ALU(self.prev.ex_control['ALUOp'])
        if self.prev.ex_control['ALUSrc'] == 0:
            zero, alu_out = alu.compute(A, B)
        else:
            zero, alu_out = alu.compute(A, Binary(code = self.prev.imm).get_decimal())
        self.zero = zero
        self.ALUOut = alu_out 

        #Branch
        im = Binary(code = self.prev.imm)
        im.sl_bits(2)
        self.branch_tg = im.get_decimal() + self.prev.pc
        if self.mem_control['Branch'] == 1 and self.__ex_mem['zero'] == 1: #BEQ
            self.mem_control['branch_aux'] = 1   #indica que houve desvio e as prox. instruções no pipeline serão canceladas