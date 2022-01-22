class Binary:

    def __init__(self, code = None, decimal = None, bits = 0):
        if code:
            self.__code = code.strip()  
        else:
            if decimal < 0:
                self.__code = bin(((decimal * -1) - 1) ^ 0xFFFFFFFF)[2:]
                #bin(~decimal-1)[2:].rjust(bits, '1')
            else:
                self.__code = bin(decimal)[2:].zfill(bits)
        self.__signal_bit = self.__code[0]
        self.__unsigned = self.__code[1:]


    def get_decimal(self):
        if self.__signal_bit == '0':
            return int(self.__code, 2)
        else:
            return -1 * ((int(self.__code, 2) ^ 0xFFFFFFFF) + 1)
    
    
    def get_code(self):
        return self.__code

    def sl_bits(self, bit_shifts):
        bit_num = len(self.__code)
        number = self.get_decimal()
        number = number << bit_shifts
        if number < 0:
            self.__code = bin(((number * -1) - 1) ^ 0xFFFFFFFF)[2:]
        else:
            self.__code = bin(number)[2:].zfill(bit_num)


    def sign_extend(self, bit_num, inplace = False):
        if bit_num < len(self.__code):
            return self.__code
        if inplace: 
            self.__code = self.__code.rjust(bit_num, self.__signal_bit)    
        return self.__code.rjust(bit_num, self.__signal_bit) #Adiciona à esquerda o bit de sinal, quantas vezes forem necessárias