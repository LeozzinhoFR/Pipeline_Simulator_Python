from binary import Binary
from ALU import ALU

class EX_MEM:
    def __init__(self, prev):
        self.prev = prev #Registrador ID_EX

        #Registradores
        self.empty() #Cria o registrador com valores e sinais de controle vazios

    def empty(self): 
        self.pc = 0
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
            'n_Branch' : 0,
            'Branch': 0,
            'uncond_jump' : 0, #Sinal para liberar desvio incondicional
            'jr' : 0, #Sinal para liberar desvio via instrução R (jr)
            'branch_aux': 0, #Sinal de controle a mais para facilitar manipulação de tratamento de hazard de controle
            'MemRead': 0,
            'MemWrite': 0
        }
            
    def send_info(self, replace_a, replace_b, out): #Dados do parâmetros do pipeline passado são calculados e passados para um novo
        #Valores passados diretamente de um registrador ao outro
        self.wb_control = self.prev.wb_control
        self.pc = self.prev.pc
        self.mem_control = self.prev.mem_control
        self.B = self.prev.B

        #Variáveis temporárias para fazer o cálculo na ALU
        A = self.prev.A 
        B = self.prev.B

        #Hazard de dados
        if replace_a == 1:
            A = out
        if replace_b == 1:
            B = out

        #Definir registrador destino
        reg_dst = self.prev.ex_control['RegDst']
        if reg_dst == 1:
            self.RD = self.prev.RD
        elif reg_dst == 0:
            self.RD = self.prev.RT
        else:
            self.RD = '11111' #Caso específico do JAL

        #Cálculos da ALU
        alu = ALU(self.prev.ex_control['ALUOp'])

        if self.prev.ex_control['ALUSrc'] == 0:
            zero, alu_out = alu.compute(A, B, Binary(code = self.prev.sa).get_decimal())
        else:
            zero, alu_out = alu.compute(A, Binary(code = self.prev.imm).get_decimal(), Binary(code = self.prev.sa).get_decimal())
        self.zero = zero
        self.ALUOut = alu_out 


        # No EX_MEM após determinar se branch foi tomado
        actual_taken = (self.mem_control['Branch'] == 1 and self.zero == 1) or \
                    (self.mem_control['n_Branch'] == 1 and self.zero == 0)
        self.branch_predictor.update(self.pc, actual_taken)

        #Branch
        if self.mem_control['jr'] == 1: 
            self.branch_tg = A
            return

        im = Binary(code = self.prev.imm)
        im.sl_bits(2)
        self.branch_tg = im.get_decimal() + self.prev.pc
        #BEQ e BNE
        if (self.mem_control['Branch'] == 1 and self.zero == 1) or (self.mem_control['n_Branch'] == 1 and self.zero == 0):
            self.mem_control['branch_aux'] = 1   #indica que houve desvio e as prox. instruções no pipeline serão canceladas