from binary import Binary

class ID_EX:
    def __init__(self, prev):
        self.prev = prev #Registrador IF_ID
        self.empty() #Cria o registrador com valores e sinais de controle vazios

    def empty(self): 
        self.A = 0
        self.B = 0
        self.RT = 0
        self.RD = 0
        self.imm = '0'
        self.pc = 0
        self.jump = '00000000000000000000000000'
        self.sa = '00000'
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
        self.ex_control = {
            'RegDst': 0,
            'ALUSrc': 0,
            'ALUOp': '000'
        }

    def send_info(self, registers): #Dados do registrador passado são decodificados e registrados 
        #Dados provenientes do IF_ID
        self.pc = self.prev.pc
        instruction = self.prev.instruction
        i_code = instruction.get_code() #String do número binário para decodifação

        self.imm = Binary(code = i_code[16:]).sign_extend(32)
        self.sa = i_code[21:26]
        
        #Dados de controle calculados
        opcode = i_code[:6]
        func = i_code[-6:]
        self.wb_control, self.mem_control, self.ex_control, i_type = self.control_signals()

        #Campos de registradores calculados
        rs = i_code[6:11]
        self.A = registers[rs]
        self.RT = i_code[11:16]
        self.B = registers[self.RT]
        self.RD = i_code[16:21]
        self.jump = i_code[6:]
        return rs, self.RT, i_type #Retorna rs, rt e tipo de instrução para checar hazard de dados no pipeline



    def control_signals(self):
        instruction = self.prev.instruction.get_code()
        opcode = instruction[:6]
        func = instruction[-6:]

        if opcode == '000000': #Tipo R
            wb_control = {
                'MemtoReg': 0,
                'RegWrite': 1
            }

            mem_control = {
                'n_Branch' : 0,
                'Branch': 0,
                'uncond_jump' : 0, #Sinal para liberar desvio incondicional
                'jr' : 0, #Sinal para liberar desvio via instrução R (jr)
                'MemRead': 0,
                'MemWrite': 0,
                'branch_aux': 0
            }
            
            ex_control = {
                'RegDst': 1,
                'ALUSrc': 0,
                'ALUOp': '110' #ALUOp de soma por padrão, outras instruções alteram o valor aqui
            }

            if func == '100000': #ADD
                ex_control['ALUOp'] = '010'
            elif func == '100010': #SUB
                ex_control['ALUOp'] = '110'
            elif func == '100100': #AND:
                ex_control['ALUOp'] = '000'
            elif func == '100101': #OR
                ex_control['ALUOp'] = '001'
            elif func == '101010': #SLT
                ex_control['ALUOp'] = '111'
            elif func == '000000': #SLL
                ex_control['ALUOp'] = '100'
            elif func == '001000': #JR
                wb_control['RegWrite'] = 0
                mem_control['jr'] = 1
                
            return (wb_control, mem_control, ex_control, 'r')

        elif opcode == '001000': #addi
            return ({
                'MemtoReg': 0,
                'RegWrite': 1
            },
            {
                'n_Branch' : 0,
                'Branch': 0,
                'uncond_jump' : 0, #Sinal para liberar desvio incondicional
                'jr' : 0, #Sinal para liberar desvio via instrução R (jr)
                'MemRead': 0,
                'MemWrite': 0,
                'branch_aux': 0
            },
            {
                'RegDst': 0,
                'ALUSrc': 1,
                'ALUOp': '010'
            },
            'i')
        elif opcode == '100011': #LW
            return ({
                'MemtoReg': 1,
                'RegWrite': 1
            },
            {
                'n_Branch' : 0,
                'Branch': 0,
                'uncond_jump' : 0, #Sinal para liberar desvio incondicional
                'jr' : 0, #Sinal para liberar desvio via instrução R (jr)
                'MemRead': 1,
                'MemWrite': 0,
                'branch_aux': 0
            },
            {
                'RegDst': 0,
                'ALUSrc': 1,
                'ALUOp': '010'
            },
            'i')
        elif opcode == '101011': #SW
            return ({
                'MemtoReg': 0,
                'RegWrite': 0
            },
            {
                'n_Branch' : 0,
                'Branch': 0,
                'uncond_jump' : 0, #Sinal para liberar desvio incondicional
                'jr' : 0, #Sinal para liberar desvio via instrução R (jr)
                'MemRead': 0,
                'MemWrite': 1,
                'branch_aux': 0
            },
            {
                'RegDst': 0,
                'ALUSrc': 1,
                'ALUOp': '010'
            },
            'i')
        elif opcode == '000100': #BEQ
            return ({
                'MemtoReg': 0,
                'RegWrite': 0
            },
            {
                'n_Branch' : 0,
                'Branch': 1,
                'uncond_jump' : 0, #Sinal para liberar desvio incondicional
                'jr' : 0, #Sinal para liberar desvio via instrução R (jr)
                'MemRead': 0,
                'MemWrite': 0,
                'branch_aux': 0
            },
            {
                'RegDst': 0,
                'ALUSrc': 0,
                'ALUOp': '010'
            },
            'j')
        elif opcode == '000101': #BNE
            return ({
                'MemtoReg': 0,
                'RegWrite': 0
            },
            {
                'n_Branch' : 1,
                'Branch': 0,
                'uncond_jump' : 0, #Sinal para liberar desvio incondicional
                'jr' : 0, #Sinal para liberar desvio via instrução R (jr)
                'MemRead': 0,
                'MemWrite': 0,
                'branch_aux': 0
            },
            {
                'RegDst': 0,
                'ALUSrc': 0,
                'ALUOp': '010'
            },
            'j')
        elif opcode == '000010': #Jump
            return ({
                'MemtoReg': 0,
                'RegWrite': 0
            },
            {
                'n_Branch' : 0,
                'Branch': 0,
                'uncond_jump' : 1, #Sinal para liberar desvio incondicional
                'jr' : 0, #Sinal para liberar desvio via instrução R (jr)
                'MemRead': 0,
                'MemWrite': 0,
                'branch_aux': 0
            },
            {
                'RegDst': 0,
                'ALUSrc': 0,
                'ALUOp': '000'
            },
            'j')
        elif opcode == '000011': #JAL
            return ({
                'MemtoReg': 2,
                'RegWrite': 1
            },
            {
                'n_Branch' : 0,
                'Branch': 0,
                'uncond_jump' : 1, #Sinal para liberar desvio incondicional
                'jr' : 0, #Sinal para liberar desvio via instrução R (jr)
                'MemRead': 0,
                'MemWrite': 0,
                'branch_aux': 0
            },
            {
                'RegDst': 2,
                'ALUSrc': 0,
                'ALUOp': '000'
            },
            'j')