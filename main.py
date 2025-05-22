
#Etapa de preparação de variáveis
import os
from pipeline import Pipeline
from binary import Binary


initial_address = 0 #Endereço da primeira instrução
instruction_memory = {} #Dicionário para associar uma instrução a um endereço
i = 0 # Índice para orientar endereçamento

test_programs = {
    '1': {
        'name': 'Programa 1: Básico com Hazards',
        'instructions': [
            '00000010010100111000100000100000',  # add $s1, $s2, $s3
            '00000010001101011010000000011000',  # mul $s4, $s1, $s5
            '10001111110111100000000000000000',  # lw $s6, 0($s7)
            '10101111110111100000000000000100',  # sw $s6, 4($s7)
            '00010010001101000000000000001000',  # beq $s1, $s4, target
            '00000010010100101001000000100010',  # sub $s2, $s2, $s2
            '00001000000000000000000000001100',  # j end
            '00000010011100111001100000011000',  # mul $s3, $s3, $s3 (target)
            '00000000000000000000000000000000'   # nop (end)
        ]
    },
    '2': {
        'name': 'Programa 2: Loop com Dependências',
        'instructions': [
            '00000010000100011000000000100000',  # add $s0, $s0, $s1
            '00000010000100111001000000011000',  # mul $s2, $s0, $s3
            '00000010100100101010000000100010',  # sub $s4, $s4, $s2
            '00010010100000000000000000000011',  # beq $s4, $zero, loop
            '00001000000000000000000000000110',  # j end
            '00000010001100011000100000100000',  # add $s1, $s1, $s1 (loop)
            '00001000000000000000000000000000',  # j start
            '00000000000000000000000000000000'   # nop (end/start)
        ]
    },
    '3': {
        'name': 'Programa 3: Acesso Intensivo à Memória',
        'instructions': [
            '10001110000100010000000000000000',  # lw $s1, 0($s0)
            '10001110000100100000000000000100',  # lw $s2, 4($s0)
            '00000010001100101001100000011000',  # mul $s3, $s1, $s2
            '10101110000100110000000000001000',  # sw $s3, 8($s0)
            '00001000000000000000000000000100',  # j end
            '00000000000000000000000000000000'   # nop (end)
        ]
    }
}

def main():
    print("Simulador de Pipeline MIPS\n")
    print("Programas de teste disponíveis:")
    for key, program in test_programs.items():
        print(f"({key}) {program['name']}")
    
    choice = input("\nEscolha o programa para executar (1-3) ou 4 para sair: ")
    
    if choice == '4':
            print("Encerrando simulador...")
            return
    elif choice not in test_programs:
        print("Opção inválida!")
        return
    else:
        instructions = test_programs[choice]['instructions']
        print(f"\nExecutando {test_programs[choice]['name']}")
    
    # Carregar instruções na memória
    instruction_memory = {}
    for i, instr in enumerate(instructions):
        instruction_memory[i*4] = Binary(instr)
    
    # Inicializar pipeline
    p = Pipeline(instruction_memory)
    
    # Menu de execução
    while True:
        option = input('''
        Opções de execução:
        (1) Execução passo a passo
        (2) Execução direta
        (3) Escolher outro programa
        (4) Sair
        Escolha: ''')
        
        if option == '1':
            p.run(True)
        elif option == '2':
            p.run(False)
        elif option == '3':  # Reinicia o programa
            break
        elif option == '4':
            print("Encerrando simulador...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()