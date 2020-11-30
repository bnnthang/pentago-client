from gamenode import *


oo = 1000000000000000000


class Minimax:
    """
    Minimax engine
    """

    def __init__(self, maxDepth: int=4) -> None:
        """
        Constructor

        Args:
        - maxDepth: the maximum layers to explore
        """
        self.maxDepth = maxDepth
        self.history = dict()
    
    def traverse(self, state: int, alpha=-oo, beta=oo, depth=0):
        if state in self.history:
            return self.history[state]
        
        if depth == self.maxDepth:
            self.history[state] = Node(state).eval()
            return self.history[state]
        
        winner = Node(state).terminal()
        if winner == 0:
            self.history[state] = 462
            return self.history[state]
        elif winner >= 0:
            if winner == Node(state).getTurn():
                self.history[state] = oo
            else:
                self.history[state] = -oo
            return self.history[state]
        
        if depth % 2 == 0:
            value = -oo
            for nextState in Node(state).possibleNextStates():
                value = max(value, self.traverse(nextState, alpha, beta, depth + 1))
                alpha = max(alpha, value)
                if alpha >= beta:
                    self.history[state] = oo
                    break
            self.history[state] = value
        else:
            value = oo
            for nextState in Node(state).possibleNextStates():
                value = min(value, self.traverse(nextState, alpha, beta, depth + 1))
                beta = min(beta, value)
                if alpha >= beta:
                    self.history[state] = -oo
                    break
            self.history[state] = value
        
        if depth > 0:
            return value
        else:
            bestValue, bestState = -oo * 10, None
            for nextState in Node(state).possibleNextStates():
                if bestValue < self.history[nextState]:
                    bestValue, bestState = self.history[nextState], nextState
            return bestState
        
    def run(self, state):
        self.history.clear()
        nextState = self.traverse(state)
        return nextState


if __name__ == "__main__":
    import time
    start_time = time.time()
    mnm = Minimax(3)
    # print(mcts.run(259461630))
    # print(mnm.traverse(5115112716510))
    print(mnm.run(4782969))
    print("--- %s seconds ---" % (time.time() - start_time))