class ALU:
    
    def __init__(self, code):
        self.__code = code

    def compute(self, A, B):
        zero = int(A==B)
        if self.__code == '010': #SOMA
            return zero, A+B
        else:
            return 0, 0 #Não é pra vir aqui