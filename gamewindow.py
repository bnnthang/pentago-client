from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from boardwidget import MyWidget, BoardWidget
from gamenode import Node
from gamelog import GameLog

import sys


class GameWindow(QMainWindow):
    """
    Main game window
    """

    # class attributes
    MIN_WIDTH = 987
    MIN_HEIGHT = 678

    # signal
    closing = pyqtSignal()
    chatSending = pyqtSignal(str)
    gameEnded = pyqtSignal(str)

    def __init__(self, player1="", player2="", revertible=True):
        """
        Constructor
        """
        super().__init__()
        self.initUI(player1, player2, revertible)
    
    def initUI(self, player1, player2, revertible):
        """
        Initialize components
        """
        # set look
        self.setWindowTitle("Pentago")
        self.setObjectName("mainwnd")
        self.setStyleSheet("#mainwnd { background: saddlebrown; }")
        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMinimumHeight(self.MIN_HEIGHT)
        self.setWindowIcon(QIcon("img/tic-tac-toe.png"))
        # create main widget and layout
        self.setCentralWidget(MyWidget())
        self.centralWidget().setLayout(QHBoxLayout())
        # create game log
        self.gamelog = GameLog(self.centralWidget(), player1, player2, revertible)
        self.centralWidget().layout().addWidget(self.gamelog)
        # create board
        self.board = BoardWidget(self.centralWidget())
        bcontainer = MyWidget()
        bcontainer.setLayout(QHBoxLayout())
        bcontainer.layout().addWidget(self.board)
        self.centralWidget().layout().addWidget(bcontainer)
        # create status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().setStyleSheet("background: lightgray;") # set background color
        self.statusBar().showMessage("Welcome!", 3000)
        # connect signals
        self.board.finishMove.connect(self.gameflow) # connect signal to manage game flow
        self.gamelog.enableMoves.connect(self.enableFlow)
        self.gamelog.disableMoves.connect(self.board.setDisable)
        self.gamelog.stateChanged.connect(self.board.setState)
        self.gamelog.statusChanged.connect(self.statusBar().showMessage)
        self.gamelog.previewEvent.connect(self.board.tempState)
        # hooking
        self.board.hookTurn(self.gamelog.getTurn) # hook to get turn
    
    def disableFlow(self):
        self.board.setDisable()
        self.gamelog.previewButton.setEnabled(False)
        self.gamelog.getbackButton.setEnabled(False)
        self.gamelog.revertButton.setEnabled(False)
    
    def enableFlow(self):
        self.board.setEnable()
        self.gamelog.previewButton.setEnabled(True)
        self.gamelog.getbackButton.setEnabled(True)
        self.gamelog.revertButton.setEnabled(True)
    
    def gameflow(self):
        """
        Manage the game flow. Default for local PvP play.
        """
        # temporary disable moves
        self.board.setDisable()
        # find winner
        winner = Node(self.board.getState()).terminal()
        msg = None
        # if game ended
        if winner == 0:
            msg = "> Game tied."
        elif winner == 1:
            msg = "> Black won!"
        elif winner == 2:
            msg = "> White won!"
        self.gamelog.moveDecided(self.board.getState(), msg)
    
    def closeEvent(self, a0: QCloseEvent):
        self.closing.emit()
        super().closeEvent(a0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = GameWindow("Black", "White")
    wnd.show()
    sys.exit(app.exec())