#Etapa de preparação de variáveis

from pipeline import Pipeline
from binary import Binary


initial_address = 0 #Endereço da primeira instrução
instruction_memory = {} #Dicionário para associar uma instrução a um endereço
i = 0 # Índice para orientar endereçamento

code_lines = ''

#print(-1 * ((int('11111111111111111111111111111111', 2) ^ 0xFFFFFFFF) + 1))


filename = input('\nDigite o nome do arquivo. Caso queira fazer a entrada via teclado, insira -1 como entrada.\n')

if(filename == '-1'):
    code = input('Insira o código de máquina')
    code_lines = code.splitlines() #linhas são dadas pelo input do usuário
else:
    try: 
        code = open('PipelineSimulator/'+filename, 'r') 
        code_lines = code.readlines() #linhas são dadas pela separação do arquivo de input
    except:
        print('Arquivo de entrada não encontrado')
        exit()

for l in code_lines: 
    instruction_memory[initial_address+i*4] = Binary(l) # Adiciona uma instrução em um endereço separado por 4 bytes
    i+=1


#Etapa para interação com usuário:

choice = input('''
(1) Execução passo a passo
(2) Execução direta
(3) Reset
Outras entradas causarão o fechamento do simulador.
''')

if choice == '1':
    #------------EXECUÇÃO PASSO A PASSO------------
    for i in instruction_memory:
        print(instruction_memory[i].get_code(), end = '\t')
    p = Pipeline(instruction_memory)
    p.run()

