class ALU:
    
    def __init__(self, code):
        self.code = code

    def compute(self, A, B, sa):
        zero = int(A==B)
        if self.code == '010': #SOMA
            return zero, A+B
        elif self.code == '110': #SUBTRAÇÃO
            return zero, A-B
        elif self.code == '000': #AND
            return zero, A&B
        elif self.code == '001': #OR
            return zero, A|B
        elif self.code == '111': #SLT
            print('A: '+str(A))
            print('B: '+str(B))
            return zero, int(A < B)
        elif self.code == '100': #SLL
            return zero, B << sa
        
        elif self.code == '011':  # MUL (multi-ciclo)
            if not hasattr(self, 'mul_stage'):
                self.mul_stage = 0
                self.mul_A = A
                self.mul_B = B
                self.mul_result = 0
                return zero, None  # Indica que precisa de mais ciclos
            self.mul_stage += 1
            if self.mul_stage == 1:
                # Estágio 1 - preparação
                return zero, None
            elif self.mul_stage == 2:
                # Estágio 2 - multiplicação
                self.mul_result = self.mul_A * self.mul_B
                return zero, self.mul_result

        else:
            return 0, 0 #Não é pra vir aqui