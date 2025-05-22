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
    


    def to_assembly(self):
        opcode = self.__code[:6]
        rs = self.__code[6:11]
        rt = self.__code[11:16]
        rd = self.__code[16:21]
        shamt = self.__code[21:26]
        funct = self.__code[26:]
        imm = str(self.get_decimal())
        
        if opcode == '000000':  # Tipo R
            if funct == '100000': return f"add ${int(rd,2)}, ${int(rs,2)}, ${int(rt,2)}"
            elif funct == '100010': return f"sub ${int(rd,2)}, ${int(rs,2)}, ${int(rt,2)}"
            elif funct == '100100': return f"and ${int(rd,2)}, ${int(rs,2)}, ${int(rt,2)}"
            elif funct == '100101': return f"or ${int(rd,2)}, ${int(rs,2)}, ${int(rt,2)}"
            elif funct == '101010': return f"slt ${int(rd,2)}, ${int(rs,2)}, ${int(rt,2)}"
            elif funct == '000000': return f"sll ${int(rd,2)}, ${int(rt,2)}, {int(shamt,2)}"
            elif funct == '000110': return f"mul ${int(rd,2)}, ${int(rs,2)}, ${int(rt,2)}"
        elif opcode == '100011': return f"lw ${int(rt,2)}, {imm}(${int(rs,2)})"
        elif opcode == '101011': return f"sw ${int(rt,2)}, {imm}(${int(rs,2)})"
        elif opcode == '000100': return f"beq ${int(rs,2)}, ${int(rt,2)}, {imm}"
        elif opcode == '000010': return f"j {int(self.__code[6:], 2)}"
        return self.__code  # Padrão se não reconhece
    
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