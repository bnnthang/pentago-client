from PyQt5.QtCore import *
from gamewindow import GameWindow
from minimax import Minimax


class BotEngine(QThread):
    """
    Subclass to run engine concurrently
    """

    # signal
    finished = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        # self.botEngine = MCTS(1234)
        self.botEngine = Minimax(3)
    
    def setState(self, state):
        self.state = state
    
    def run(self):
        nextState = self.botEngine.run(self.state)
        print(nextState, "shite")
        self.finished.emit(nextState)


class GameWithBot(GameWindow):

    def __init__(self, player1="", player2="", botTurn=False):
        super().__init__(player1, player2, True)
        # init bot
        self.botTurn = botTurn
        self.botEngine = BotEngine()
        self.botEngine.finished.connect(self.botMakeMove)
        # show
        self.show()
        # run if bot starts
        if self.botTurn == self.gamelog.currentTurn:
            # make sure to disable moves
            self.board.setDisable()
            # run engine
            self.botEngine.setState(self.board.getState())
            self.botEngine.start()
            self.statusBar().showMessage("Thinking...")

    @pyqtSlot(object)
    def botMakeMove(self, nextState):
        # set next state
        self.board.setState(nextState)
        self.board.finishMove.emit()
        self.statusBar().showMessage("Decided", 3000)

    def gameflow(self):
        """
        Overload game flow managing function
        """
        # handle normally
        super().gameflow()
        # if it is bot turn
        if self.gamelog.currentTurn == self.botTurn:
            # make sure to disable moves
            self.board.setDisable()
            # run engine
            self.botEngine.setState(self.board.getState())
            self.botEngine.start()
            self.statusBar().showMessage("Thinking...")
            

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    clgt = GameWithBot("Black", "White", True, False)
    sys.exit(app.exec())