# Simulador de Pipeline MIP
![GitHub](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.x-green)

Um simulador didático de pipeline MIPS desenvolvido em Python para o meio Acadêmico, disciplina de Arquitetura de Computadores. Este projeto implementa um processador MIPS de 5 estágios com tratamento de hazards e predição de desvios.

## 📋 Funcionalidades Principais

- **Pipeline de 5 estágios**: IF, ID, EX, MEM, WB
- **Hazard Detection**: Tratamento de hazards estruturais, de dados e de controle
- **Forwarding Unit**: Implementação completa de forwarding para evitar stalls
- **Branch Prediction**: Preditor de 2 bits com histórico de branches
- **Instruções suportadas**:
  - Aritméticas: ADD, SUB, MUL, AND, OR, SLT
  - Memória: LW, SW
  - Controle: BEQ, BNE, J, JAL, JR
- **Estatísticas**: Contagem de ciclos, stalls e métricas de branch prediction

## 🛠️ Estrutura do Código

```
├── ALU.py               # Unidade Lógica Aritmética
├── EX_MEM.py            # Registrador EX/MEM
├── ID_EX.py             # Registrador ID/EX
├── IF_ID.py             # Registrador IF/ID
├── MEM_WB.py            # Registrador MEM/WB
├── binary.py            # Manipulação de instruções binárias
├── branchPredictor.py   # Implementação do preditor de branches
├── main.py              # Interface principal e programas de teste
├── pipeline.py          # Implementação do pipeline principal
```

## ▶️ Como Executar

1. Clone o repositório:
```bash
git clone https://github.com/LeozzinhoFR/Pipeline_Simulator_Python.git
cd simulador-pipeline-mips
```

2. Execute o programa principal:
```bash
python main.py
```

3. Escolha um dos programas de teste disponíveis:
   - Programa 1: Básico com Hazards
   - Programa 2: Loop com Dependências
   - Programa 3: Acesso Intensivo à Memória

4. Selecione o modo de execução:
   - Passo a passo (verbose)
   - Execução direta

## 📊 Saída do Programa

O simulador fornece informações detalhadas em cada ciclo:
- Estado atual do pipeline
- Conteúdo dos registradores
- Memória de dados
- Estatísticas de execução
- Detecção de hazards e forwarding

Exemplo de saída:
```
Ciclo de clock atual: 5
Estágio de IF: 00000010010100111000100000100000 | add $s1, $s2, $s3
Estágio de ID: 00000010001101011010000000011000 | mul $s4, $s1, $s5
...
Banco de registradores:
$s0: 0
$s1: 20
$s2: 30
...
=== Estatísticas ===
Total de ciclos: 5
Stalls inseridos: 1
Branches tomados: 0
Predições incorretas: 0
```

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ✉️ Contato

Se tiver dúvidas ou sugestões, entre em contato pelo email: [seu-email@exemplo.com](mailto:seu-email@exemplo.com)
