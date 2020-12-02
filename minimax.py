from gamenode import *


oo = 1000000000000000000


class Minimax:
    """
    Minimax engine
    """

    MAX_DEPTH = 4
    GOOD_MOVES_LIMIT = 19
    BETTER_MOVES_LIMIT = 7

    def __init__(self) -> None:
        """
        Constructor

        Args:
        - maxDepth: the maximum layers to explore
        """
        self.history = dict()
        self.cacheEval = dict()
    
    def traverse(self, state: int, alpha=-oo, beta=oo, depth=0):
        # return if visited
        if state in self.history:
            return self.history[state]

        # check terminality
        winner = Node(state).terminal()
        if winner == 0:
            self.history[state] = 567
            return self.history[state]
        elif winner >= 0:
            if winner == Node(state).getTurn():
                self.history[state] = oo
            else:
                self.history[state] = -oo
            return self.history[state]
        
        def preeval(x):
            if x not in self.cacheEval:
                self.cacheEval[x] = Node(x).eval()
            return self.cacheEval[x]
        
        # return if reached max depth
        if depth >= self.MAX_DEPTH:
            self.history[state] = preeval(state)
            return self.history[state]
        
        # consider only some best next moves
        nextStates = Node(state).possibleNextStates()

        nextStates.sort(key=preeval)
        goodStates = nextStates[:self.GOOD_MOVES_LIMIT]
        for i in nextStates[self.GOOD_MOVES_LIMIT:]:
            self.history[i] = preeval(i)
        
        if depth % 2 == 0:
            value = -oo
            for i in range(len(goodStates)):
                if alpha < beta:
                    value = max(value, self.traverse(goodStates[i], alpha, beta, depth + 1 if i < self.BETTER_MOVES_LIMIT else depth + 2))
                    alpha = max(alpha, value)
            self.history[state] = value
        else:
            value = oo
            for i in range(len(goodStates)):
                if alpha < beta:
                    value = min(value, self.traverse(goodStates[i], alpha, beta, depth + 1 if i < self.BETTER_MOVES_LIMIT else depth + 2))
                    beta = min(beta, value)
            self.history[state] = value
        
        if depth > 0:
            return value
        else:
            bestValue, bestState = oo * 10, None
            for nextState in nextStates:
                if nextState in self.history and bestValue > self.history[nextState]:
                    bestValue, bestState = self.history[nextState], nextState
            return bestState
    
    def run(self, state):
        self.history.clear()
        return self.traverse(state)


if __name__ == "__main__":
    import time
    start_time = time.time()
    mnm = Minimax()
    # print(mcts.run(259461630))
    # print(mnm.traverse(5115112716510))
    print(mnm.run(0))
    print("--- %s seconds ---" % (time.time() - start_time))
