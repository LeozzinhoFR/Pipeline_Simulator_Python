class BranchPredictor:
    def __init__(self):
        self.predict_table = {}  # PC -> estado (00 a 11)
        self.stats = {'hits': 0, 'misses': 0}
    
    def predict(self, pc):
        # Estado inicial se não encontrado: Weakly Not Taken (01)
        state = self.predict_table.get(pc, 1)
        return state >= 2  # Taken se estado >= 2 (10 ou 11)
    
    def update(self, pc, taken):
        state = self.predict_table.get(pc, 1)
        
        # Atualiza estado
        if taken:
            state = min(state + 1, 3)  # Incrementa até 11
        else:
            state = max(state - 1, 0)  # Decrementa até 00
        
        # Atualiza estatísticas
        predicted_taken = state >= 2
        if predicted_taken == taken:
            self.stats['hits'] += 1
        else:
            self.stats['misses'] += 1
            
        self.predict_table[pc] = state
    
    def get_accuracy(self):
        total = self.stats['hits'] + self.stats['misses']
        return (self.stats['hits'] / total * 100) if total > 0 else 0