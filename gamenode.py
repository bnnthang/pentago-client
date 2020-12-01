from data import *


def getDigit(a: int, i: int, basePow: list) -> int:
    """
    Get the i-th digit of a given value

    Args:
    - a: given value to get from
    - i: the position wanted
    - base_pow: the base power list

    Return:
    - The i-th digit
    """
    return a // basePow[i] % basePow[1]


class Node:
    """
    Represent a state of the game
    """

    # attributes
    displayOrder = [
        [(1, 0), (1, 1), (1, 2), (-1, -1), (0, 0), (0, 1), (0, 2)],
        [(1, 3), (1, 4), (1, 5), (-1, -1), (0, 3), (0, 4), (0, 5)],
        [(1, 6), (1, 7), (1, 8), (-1, -1), (0, 6), (0, 7), (0, 8)],
        [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(2, 0), (2, 1), (2, 2), (-1, -1), (3, 0), (3, 1), (3, 2)],
        [(2, 3), (2, 4), (2, 5), (-1, -1), (3, 3), (3, 4), (3, 5)],
        [(2, 6), (2, 7), (2, 8), (-1, -1), (3, 6), (3, 7), (3, 8)]
    ]

    def setState(self, hashValue: int):
        self.state = hashValue

    def __init__(self, state: int = 0) -> None:
        """
        Constructor
        """
        self.setState(state)

    def getQuarter(self, index: int) -> int:
        """
        Get the state of a quarter
        """
        return getDigit(self.state, index, POW_QUARTERS)

    def getCell(self, quarter: int, cell: int) -> int:
        """
        Get the state of a cell
        """
        return getDigit(self.getQuarter(quarter), cell, POW_CELLS)

    def getState(self) -> int:
        return self.state

    def rotate(self, quarter, swapList):
        """
        Rotate a quarter
        """
        for i, j in swapList:
            vi, vj = self.getCell(quarter, i), self.getCell(quarter, j)
            self.state += (vj - vi) * POW_CELLS[i] * POW_QUARTERS[quarter]
            self.state += (vi - vj) * POW_CELLS[j] * POW_QUARTERS[quarter]

    def countEmptyCells(self) -> int:
        """
        Count empty cells
        """
        ret = 0
        for quarter in range(4):
            for cell in range(9):
                ret += self.getCell(quarter, cell) == 0
        return ret

    def getEmptyCells(self) -> list:
        """
        Get a list of all empty cells
        """
        ret = []
        for quarter in range(4):
            for cell in range(9):
                if self.getCell(quarter, cell) == 0:
                    ret.append((quarter, cell))
        return ret

    def terminal(self) -> int:
        """
        Check if the game ended

        Return:
        - -1: not ended
        - 0: tie
        - 1: black wins
        - 2: white wins
        """

        def sameColorLine(color) -> bool:
            for line in LINES_5:
                flag = True
                for quarter, cell in line:
                    if self.getCell(quarter, cell) != color:
                        flag = False
                        break
                if flag:
                    return True
            return False

        blackWon = sameColorLine(1)
        whiteWon = sameColorLine(2)

        if blackWon:
            if whiteWon:
                # game tied if both colors have 5-in-a-row
                return 0
            else:
                # black won
                return 1
        else:
            if whiteWon:
                # white won
                return 2
            else:
                if self.countEmptyCells() == 0:
                    # game tied if players cannot move
                    return 0
                else:
                    # game not ended
                    return -1

    def possibleNextStates(self) -> list:
        """
        Get all possible next states
        """
        ret = set()
        emptyCells = self.getEmptyCells()
        color = (36 - len(emptyCells)) % 2 + 1
        # cache current state
        cachedState = self.state
        # iterate through all remaining cells
        for q1, c1 in emptyCells:
            for q2 in range(4):
                for c2 in [ROTATE_CW, ROTATE_CCW]:
                    # place a new piece
                    self.state += color * POW_CELLS[c1] * POW_QUARTERS[q1]
                    # rotate
                    self.rotate(q2, c2)
                    # add to result
                    ret.add(self.getState())
                    # revert
                    self.setState(cachedState)
        return list(ret)

    def __repr__(self) -> str:
        ret = ""
        for row in self.displayOrder:
            for quarter, cell in row:
                if quarter < 0 and cell < 0:
                    ret += " "
                else:
                    ret += str(self.getCell(quarter, cell))
            ret += "\n"
        return ret

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def getTurn(self) -> int:
        """
        Get current turn

        Return:
        - 1: black
        - 2: white
        """
        return self.countEmptyCells() % 2 + 1

    def fillCell(self, quarter, cell):
        self.state += self.getTurn() * POW_CELLS[cell] * POW_QUARTERS[quarter]

    def __hash__(self) -> int:
        return self.state

    def eval(self):
        """
        Evaluation function
        """

        def getScore(color):
            winner = self.terminal()
            if winner >= 0:
                if winner == color:
                    return WEIGHT_LINES_5
                elif winner == 3 - color:
                    return -WEIGHT_LINES_5
                else:
                    return 234

            def analyzeLines(data, score):
                sumScore = 0
                for line, nullifiers in data:
                    flag = True
                    for q, c in line:
                        if self.getCell(q, c) != color:
                            flag = False
                            break
                    if flag:
                        advantage = len(nullifiers)
                        for q, c in nullifiers:
                            if self.getCell(q, c) == color:
                                advantage = 0
                                break
                            elif self.getCell(q, c) == 3 - color:
                                advantage -= 1
                        sumScore += score[advantage]
                return sumScore
            
            def analyzeCriticalCells():
                sumScore = 0
                for i in range(2):
                    for q, c in CRITICAL_CELLS[i]:
                        if self.getCell(q, c) == color:
                            sumScore += WEIGHT_CRITICAL_CELLS[i]
                return sumScore
            
            return analyzeLines(LINES_3, WEIGHT_LINES_3) + analyzeLines(LINES_4, WEIGHT_LINES_4) + analyzeCriticalCells()

        return getScore(self.getTurn()) - getScore(3 - self.getTurn())


if __name__ == "__main__":
    print(Node(67959325095502806 + 3**12))
    print(Node(67959325095502806 + 3**12).eval())
    # print(Node(98416).eval())
    # print(Node(5115370998780).eval())
    # print(Node(5115112716510))
    # print(Node(38357817300))
    # for i in Node(5115112716288).possibleNextStates():
    #     print(i)
