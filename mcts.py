from random import randint
from gamenode import *
from math import sqrt, log


oo = 1e18


class VisitLog:

    SCORES = [-0.3, 0.3, 0.9] # lose tie win

    def __init__(self, wins=0, ties=0, loses=0):
        self.wins = wins
        self.ties = ties
        self.loses = loses
    
    def totalVisits(self):
        return self.wins + self.ties + self.loses
    
    def update(self, data: tuple):
        self.wins += data[0]
        self.ties += data[1]
        self.loses += data[2]
    
    def getScore(self):
        return self.SCORES[0] * self.loses + self.SCORES[1] * self.ties + self.SCORES[2] * self.wins
    
    def UCT(self, parentVisits):
        return self.getScore() / self.totalVisits() + sqrt(2.0 * log(parentVisits) / self.totalVisits())


class HistoryData:
    
    def __init__(self, state) -> None:
        self.totalVisits = 0
        self.visitedMoves = dict()
        self.unvisitedMoves = Node(state).possibleNextStates()
    
    def haveUnvisitedMoves(self) -> bool:
        return len(self.unvisitedMoves) > 0
    
    def getUnvisitedMove(self) -> int:
        # pop from unvisited list
        move = self.unvisitedMoves.pop(-1)
        # create new entry in visited dict
        self.visitedMoves[move] = VisitLog()
        # return move
        return move
    
    def getOptimalNextMove(self):
        bestValue, bestMove = -oo, None
        # iterate through all moves
        for move in self.visitedMoves:
            # calculate uct
            uct = self.visitedMoves[move].UCT(self.totalVisits)
            # compare and update
            if uct > bestValue:
                bestValue, bestMove = uct, move
        # return
        return bestMove
    
    def update(self, childState, data: tuple):
        self.totalVisits += data[0] + data[1] + data[2]
        self.visitedMoves[childState].update(data)


class MCTS:
    """
    Monte Carlo Tree Search engine
    """
    
    # attributes
    REP = 1000 # times to repeat

    def __init__(self) -> None:
        """
        Constructor
        """
        self.history = dict()
        self.currentPath = list()
    
    def traverse(self, state):
        self.currentPath.append(state)
        if self.history[state].haveUnvisitedMoves():
            return self.history[state].getUnvisitedMove()
        nextState = self.history[state].getOptimalNextMove()
        return self.traverse(nextState)
    
    def rollout(self, state):
        currentNode = Node(state)
        winner = currentNode.terminal()
        if winner < 0:
            a, b, c, d = randint(0, 3), randint(0, 8), randint(0, 3), randint(0, 1)
            currentNode.fillCell(a, b)
            currentNode.rotate(c, ROTATE_CW if d else ROTATE_CCW)
            return self.rollout(currentNode.getState())
        else:
            return winner
    
    def backpropagation(self, previousState, records):
        # get parent
        parentState = self.currentPath.pop(-1)
        # update
        tempRecords = [records[2], records[1], records[0]]
        self.history[parentState].update(previousState, tempRecords)
        # continue
        if len(self.currentPath) > 0:
            self.backpropagation(parentState, tempRecords)
    
    def run(self, initialState: int):
        """
        Run the engine

        Args:
        - initialState: the state to start finding
        """
        self.history.clear()
        self.history[initialState] = HistoryData(initialState)
        # repeat the process
        for i in range(self.REP):
            # selection
            unvisitedState = self.traverse(initialState)
            # expansion
            self.history[unvisitedState] = HistoryData(unvisitedState)
            turn = Node(unvisitedState).getTurn()
            # simulation
            records = [0, 0, 0] # loses ties wins
            for j in range(randint(3, 7)):
                winner = self.rollout(unvisitedState)
                if winner == 0:
                    records[1] += 1
                elif winner == turn:
                    records[2] += 1
                else:
                    records[0] += 1
            # backpropagation
            self.backpropagation(unvisitedState, records)
        # choose best move
        bestValue, bestMove = -oo, None
        for move in self.history[initialState].visitedMoves:
            currentScore = self.history[initialState].visitedMoves[move].getScore()
            if bestValue < currentScore:
                bestValue, bestMove = currentScore, move
        return bestMove


if __name__ == "__main__":
    import time
    m = MCTS()
    startState = 5115112716510
    print(Node(startState))
    start_time = time.time()
    nextMove = m.run(startState)
    print(Node(nextMove))
    print("--- %s seconds ---" % (time.time() - start_time))