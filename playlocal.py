from PyQt5.QtCore import *
from gamewindow import GameWindow
from minimax import Minimax
from gamenode import Node


class BotEngine(QThread):
    """
    Subclass to run engine concurrently
    """

    # signal
    finished = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.botEngine = Minimax()
    
    def setState(self, state):
        self.state = state
    
    def run(self):
        import time
        start_time = time.time()
        nextState = self.botEngine.run(self.state)
        print("--- %s seconds ---" % (time.time() - start_time))
        self.finished.emit(nextState)


class GameWithBot(GameWindow):

    def __init__(self, player1="", player2="", botTurn=False):
        super().__init__(player1, player2, True)
        # init bot
        self.botTurn = botTurn
        self.botEngine = BotEngine()
        self.botEngine.finished.connect(self.botMakeMove)
        self.gamelog.addLog(f"You play as {'black' if botTurn else 'white'}")
        # show
        self.show()
        # run if bot starts
        if self.botTurn == self.gamelog.currentTurn:
            # make sure to disable moves
            self.board.setDisable()
            self.gamelog.revertButton.setEnabled(False)
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
        if Node(self.board.getState()).terminal() >= 0:
            self.gamelog.revertButton.setEnabled(False)
        else:
            # if it is bot turn
            if self.gamelog.currentTurn == self.botTurn:
                # make sure to disable moves
                self.board.setDisable()
                self.gamelog.revertButton.setEnabled(False)
                # run engine
                self.botEngine.setState(self.board.getState())
                self.botEngine.start()
                self.statusBar().showMessage("Thinking...")
            

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    wnd = GameWithBot("Black", "White", False)
    wnd.show()
    sys.exit(app.exec())