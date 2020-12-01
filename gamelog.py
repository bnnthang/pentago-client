from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal

from boardwidget import MyWidget
from gamenode import Node

GAMELOG_PANEL = 300


class PlayerNameplate(QLabel):
    """
    Display players' names
    """

    # class attributes
    NAMEPLATE_HEIGHT = 80

    def __init__(self, parent=None, name: str="", isWhite: bool=True) -> None:
        """
        Constructor

        Args:
        - parent: the parent widget
        - name: the player's name
        - isWhite: if the color is white
        """
        super().__init__(parent)
        # init ui
        self.initUI(name, isWhite)
    
    def initUI(self, name, isWhite):
        """
        Initialize components
        """
        # set sizes
        self.setFixedHeight(self.NAMEPLATE_HEIGHT)
        # set name
        self.setText(name)
        # alignmnet
        self.setAlignment(Qt.AlignCenter)
        # create style manager
        self.styles = [f"""
            background: {"white" if isWhite else "black"};
            color: {"black" if isWhite else "white"};
            font-size: 18px;
        """]
        self.styles.append("border: 3px solid limegreen;" + self.styles[0])
        # set normal style
        self.setStyleSheet(self.styles[0])

    
    def changeFocus(self, turn: bool):
        """
        Change the style to notify when it is the player's turn

        Args:
        - turn: whether it is the player's turn
        """
        self.setStyleSheet(self.styles[turn])


class PlayerBoard(MyWidget):
    """
    Show two player
    """

    def changeFocus(self):
        self.nameplates[0].myTurn(not self.currentTurn)
        self.nameplates[1].myTurn(self.currentTurn)
    
    def __init__(self, parent=None, player1: str="", player2: str="") -> None:
        """
        Constructor
        """
        super().__init__(parent)
        # init ui
        self.initUI(player1, player2)
    
    def initUI(self, player1, player2):
        """
        Initialize components
        """
        # set layout
        self.setLayout(QGridLayout())
        # save names
        self.names = [player1, player2]
        # create nameplates
        self.nameplates = [
            PlayerNameplate(self, player1, False), # black
            PlayerNameplate(self, player2) # white
        ]
        # add to layout
        self.layout().addWidget(self.nameplates[0], 0, 0)
        self.layout().addWidget(self.nameplates[1], 0, 1)
    
    def setFocus(self, turn):
        """
        Focus on current moving player

        Args:
        - turn: the current moving player
        """
        self.nameplates[0].changeFocus(not turn)
        self.nameplates[1].changeFocus(turn)
    
    def getName(self, id):
        return self.names[id]


class LogItem(QListWidgetItem):
    """
    Subclass to record moves
    """

    def __init__(self, parent=None, text: str="", player: int=-1, state: int=-1):
        """
        Constructor

        Args:
        - parent: the parent widget
        - text: the visible text
        - player: the actor
        - state: the saved state
        """
        super().__init__(text, parent)
        self.savedState = state
        self.player = player
    
    def isPreviousMove(self) -> bool:
        """
        Check if the log item is a previous state
        """
        return self.savedState >= 0


class GameLog(MyWidget):
    """
    Game logging
    """

    # class attributes
    GAMELOG_PANEL_WIDTH = 300
    ACTION_BUTTON_HEIGHT = 30
    STATUS_BAR_TIMEOUT = 3000

    # signals
    stateChanged = pyqtSignal(object)
    previewEvent = pyqtSignal(object)
    statusChanged = pyqtSignal(object, object)
    enableMoves = pyqtSignal()
    disableMoves = pyqtSignal()

    def __init__(self, parent=None, player1: str="", player2: str="", revertible=True):
        """
        Constructor
        """
        super().__init__(parent)
        # init attributes
        self.currentTurn = True # black goes first
        # init ui
        self.initUI(player1, player2, revertible)
        # initial move is 0
        self.moveDecided(0, "> Game started.")

    
    def initUI(self, player1, player2, revertible):
        """
        Initialize components
        """
        # create layout
        self.setFixedWidth(self.GAMELOG_PANEL_WIDTH)
        self.setLayout(QVBoxLayout())
        # player name board
        self.pnameboard = PlayerBoard(self, player1, player2)
        self.setFocus(self.currentTurn)
        self.layout().addWidget(self.pnameboard)
        # log list
        self.logList = QListWidget(self)
        self.logList.setWordWrap(True)
        self.logList.clear()
        self.logList.model().rowsInserted.connect(self.logList.scrollToBottom)
        self.layout().addWidget(self.logList)
        # chat frame
        chat_frame = MyWidget(self)
        chat_frame.setLayout(QHBoxLayout(chat_frame))
        self.msgEntry = QLineEdit(chat_frame)
        self.msgEntry.setPlaceholderText("Enter message")
        self.msgEntry.setPalette(QApplication.style().standardPalette())
        self.sendButton = QPushButton("Send", chat_frame)
        self.sendButton.setFixedWidth(50)
        self.sendButton.clicked.connect(self.sendButtonClicked)
        chat_frame.layout().addWidget(self.msgEntry)
        chat_frame.layout().addWidget(self.sendButton)
        self.layout().addWidget(chat_frame)
        # preview button
        self.previewButton = QPushButton(text="Preview")
        self.previewButton.setFixedHeight(self.ACTION_BUTTON_HEIGHT)
        self.previewButton.clicked.connect(self.previewButtonClicked)
        self.layout().addWidget(self.previewButton)
        # revert button
        self.revertButton = QPushButton(text="Revert")
        self.revertButton.setFixedHeight(self.ACTION_BUTTON_HEIGHT)
        self.revertButton.clicked.connect(self.revertButtonClicked)
        if revertible:
            self.layout().addWidget(self.revertButton)
        # get back button
        self.getbackButton = QPushButton(text="Back to current")
        self.getbackButton.setFixedHeight(self.ACTION_BUTTON_HEIGHT)
        self.getbackButton.clicked.connect(self.getbackButtonClicked)
        self.layout().addWidget(self.getbackButton)
    
    def moveDecided(self, state, specialMsg=None):
        """
        When a new move is made
        """
        # add log
        self.addLog(f"> {self.getName(self.currentTurn)} moved." if specialMsg == None else specialMsg, self.currentTurn, state)
        # alter turn
        self.currentTurn = not self.currentTurn
        # change focus
        self.pnameboard.setFocus(self.currentTurn)
        # allow moves if ok
        if Node(state).terminal() < 0:
            self.enableMoves.emit()
    
    def addLog(self, text, player=-1, state=-1):
        """
        Add item to game log

        Args:
        - text: the visible text
        - player: the actor
        - state: the saved state
        """
        # update latest state if needed
        if state >= 0:
            self.latestState = state
        # add log
        self.logList.addItem(LogItem(self.logList, text, player, state))
    
    def getName(self, id):
        return self.pnameboard.getName(id)
    
    def previewButtonClicked(self):
        try:
            # disallow new moves
            self.disableMoves.emit()
            # check validity
            if not self.logList.selectedItems()[0].isPreviousMove():    
                return
            # preview
            self.previewEvent.emit(self.logList.selectedItems()[0].savedState)
            # notify
            self.statusChanged.emit("Preview mode", 0)
        except:
            self.statusChanged.emit("Something went wrong!", self.STATUS_BAR_TIMEOUT)
    
    def getbackButtonClicked(self):
        self.stateChanged.emit(self.latestState)
        self.statusChanged.emit("Backed to current", self.STATUS_BAR_TIMEOUT)
        # allow new moves if possible
        if Node(self.latestState).terminal() < 0:
            self.enableMoves.emit()
    
    def revertButtonClicked(self):
        # get selected id
        selectedId = self.logList.selectedIndexes()[0].row()
        # check validity
        if not self.logList.item(selectedId).isPreviousMove() or self.logList.item(selectedId).player == self.currentTurn:
            self.statusChanged.emit("Cannot revert to this move!", self.STATUS_BAR_TIMEOUT)
            return
        # delete unnecessary moves
        for i in range(self.logList.count() - 1, selectedId, -1):
            if self.logList.item(i).savedState >= 0:
                self.logList.takeItem(i)
        # update latest state
        self.latestState = self.logList.item(selectedId).savedState
        # revert GUI
        self.stateChanged.emit(self.latestState)
        # notify
        self.statusChanged.emit("Reverted successfully", self.STATUS_BAR_TIMEOUT)
        # allow new moves if possible
        if Node(self.latestState).terminal() < 0:
            self.enableMoves.emit()
    
    def getMessage(self):
        """
        Return chat message
        """
        text = self.msgEntry.text()
        self.msgEntry.clear()
        return text
    
    def sendButtonClicked(self):
        msg = self.getMessage()
        # do nothing if there is no message
        if len(msg) == 0:
            return
        self.addLog(f"[{self.pnameboard.getName(self.currentTurn)}] {msg}")
    
    def getTurn(self):
        return self.currentTurn + 1


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    clgt = GameLog(player1="Black", player2="White")
    clgt.show()
    sys.exit(app.exec())