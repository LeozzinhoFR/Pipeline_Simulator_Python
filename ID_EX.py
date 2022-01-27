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
        return rs, self.RT, i_type #Retorna rs, rt e tipo de instrução para checar hazard de dados no pipeline



    def control_signals(self):
        instruction = self.prev.instruction.get_code()
        opcode = instruction[:6]
        func = instruction[-6:]

        if opcode == '000000': #Tipo R
            if func == '100000': #ADD
                return ({
                    'MemtoReg': 0,
                    'RegWrite': 1
                },
                {
                    'Branch': 0,
                    'MemRead': 0,
                    'MemWrite': 0,
                    'branch_aux': 0
                },
                {
                    'RegDst': 1,
                    'ALUSrc': 0,
                    'ALUOp': '010'
                },
                'r')
            else:
                #FAILSAFE POR ENQUANTO
                return ({
                    'MemtoReg': 0,
                    'RegWrite': 0
                },
                {
                    'Branch': 0,
                    'MemRead': 0,
                    'MemWrite': 0,
                    'branch_aux': 0
                },
                {
                    'RegDst': 0,
                    'ALUSrc': 0,
                    'ALUOp': '000'
                },
                'r')
        elif opcode == '001000': #addi
            return ({
                'MemtoReg': 0,
                'RegWrite': 1
            },
            {
                'Branch': 0,
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
        elif opcode == '000100': #BEQ
            return ({
                'MemtoReg': 0,
                'RegWrite': 0
            },
            {
                'Branch': 1,
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