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
        else:
            return 0, 0 #Não é pra vir aqui