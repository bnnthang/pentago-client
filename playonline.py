import sys
import socketio
from threading import Timer
from gamewindow import GameWindow
from gamelog import GameLog
from gamenode import Node

from boardwidget import MyWidget, BoardWidget
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QStatusBar, QHBoxLayout, QApplication


SERVER_URL = "https://pentago-server.herokuapp.com/:39891"
# SERVER_URL = "http://192.168.1.6:4602"
OPPONENT_WAIT = 34.0

sio = socketio.Client(reconnection_attempts=5, reconnection_delay=3, reconnection_delay_max=23, request_timeout=30)
myTurn = None
myName = None
moveFlag = None


class GameLogTweaked(GameLog):

    def __init__(self, parent=None, player1: str="", player2: str="", revertible=True):
        """
        Constructor
        """
        MyWidget.__init__(self, parent)
        # init attributes
        self.currentTurn = True # black goes first
        # init ui
        self.initUI(player1, player2, revertible)

    def sendButtonClicked(self):
        msg = self.getMessage()
        # do nothing if there is no message
        if len(msg) == 0:
            return
        global sio
        sio.emit("chat", f"[{myName}] {msg}")


class GameOnline(GameWindow):

    def __init__(self, player1="", player2=""):
        """
        Constructor
        """
        super().__init__(player1, player2, False)
        self.disableFlow()
    
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
        self.gamelog = GameLogTweaked(self.centralWidget(), player1, player2, revertible)
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
        self.gamelog.enableMoves.connect(self.board.setEnable)
        self.gamelog.disableMoves.connect(self.board.setDisable)
        self.gamelog.stateChanged.connect(self.board.setState)
        self.gamelog.statusChanged.connect(self.statusBar().showMessage)
        self.gamelog.previewEvent.connect(self.board.tempState)
        # hooking
        self.board.hookTurn(self.gamelog.getTurn) # hook to get turn
    
    def initConnection(self):
        global sio

        def waitTooLong():
            self.gamelog.addLog("No opponent!")
            sio.disconnect()

        timer = Timer(OPPONENT_WAIT, waitTooLong)

        @sio.event
        def connect():
            self.gamelog.addLog("Connected!", 3000)
            self.gamelog.addLog("Waiting for opponent...")

        @sio.event
        def disconnect():
            self.gamelog.addLog("Disconnected!", 3000)
            self.disableFlow()
        
        @sio.on("bmove")
        def receiveBlackMove(state):
            global sio
            global myTurn
            if myTurn:
                self.oppoMakeMove(int(state))
        
        @sio.on("wmove")
        def receiveWhiteMove(state):
            global sio
            global myTurn
            if not myTurn:
                self.oppoMakeMove(int(state))
        
        @sio.on("chat")
        def receiveChat(msg):
            self.gamelog.addLog(msg)
        
        @sio.on("role")
        def receiveRole(color):
            """
            When receive your role
            """
            global myTurn
            global myName
            global moveFlag
            myTurn = color == "white"
            myName = color.capitalize()
            moveFlag = color[0] + "move"
            # cancel wait
            timer.cancel()
            # notify
            self.gamelog.addLog(f"You are {myName}.")
            # initial move
            self.gamelog.addLog("> Game started.", self.gamelog.currentTurn, 0)
            # alter turn
            self.gamelog.currentTurn = not self.gamelog.currentTurn
            # change focus
            self.gamelog.pnameboard.setFocus(self.gamelog.currentTurn)
            # enable functions
            self.enableFlow()
            if self.gamelog.currentTurn != myTurn:
                self.board.setDisable()

        try:
            timer.start()
            sio.connect(SERVER_URL)
        except socketio.exceptions.ConnectionError:
            # sio.connect(SERVER_URL)
            # sio.disconnect()
            self.statusBar().showMessage("Error occurred. Please close and try again.", 5000)
    
    def gameflow(self):
        """
        Overload game flow managing function
        """
        global sio
        # if it is my turn
        if self.gamelog.currentTurn == myTurn:
            # send state to server
            sio.emit(moveFlag, str(self.board.getState()))
        # handle normally
        super().gameflow()
        self.board.setDisable()
        # if now is my turn
        if Node(self.board.getState()).terminal() < 0 and self.gamelog.currentTurn == myTurn:
            # allow moves
            self.board.setEnable()
    
    def closeEvent(self, a0: QCloseEvent) -> None:
        global sio
        sio.disconnect()
        super().closeEvent(a0)
    
    def oppoMakeMove(self, newState):
        self.board.setState(newState)
        self.statusBar().clearMessage()
        self.board.finishMove.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = GameOnline("Black", "White")
    wnd.show()
    wnd.initConnection()
    app.exec()