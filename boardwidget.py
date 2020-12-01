from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from gamenode import getDigit
from data import ROTATE_CW, ROTATE_CCW, POW_CELLS, POW_QUARTERS


# constants for cells
CELL_RADIUS = 22

# constants for quarters
QUARTER_SIZE = 175

# constants for board
BOARD_SIZE_0 = 374
BOARD_SIZE_1 = 566
ROTATE_BUTTONS_SIZE = 30


def colorFromIndex(index):
    if index == 0:
        return "darkred"
    elif index == 1:
        return "black"
    else:
        return "white"


class MyWidget(QWidget):
    """
    Subclass for QWidget to handle stylesheet
    """

    def paintEvent(self, pe):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def __init__(self, parent=None):
        super().__init__(parent)


class CellWidget(MyWidget):
    """
    Class to simulate a cell
    """

    # Signals
    rotationPhase = pyqtSignal()

    def __init__(self, parent: QWidget=None, index: int=0):
        """
        Constructor

        Args:
        - index: the cell index
        - parent: the parent widget
        """
        super().__init__(parent)

        # init variables
        self.state = 0
        self.index = index
        self.enabled = True

        # init look
        self.setStyleSheet(f"""
            border: 3px solid darkred;
            border-radius: {CELL_RADIUS}px;
            background: darkred;
        """)
        self.setGeometry(0, 0, CELL_RADIUS * 2, CELL_RADIUS * 2)

        # enable event filter
        self.installEventFilter(self)
    
    def pressed(self):
        # change properties
        self.state = self.pGetTurn()
        # change look
        self.setStyleSheet(f"""
            border: 3px solid darkred;
            border-radius: {CELL_RADIUS}px;
            background: {colorFromIndex(self.state)};
        """)
        # emit signal
        self.rotationPhase.emit()
    
    def eventFilter(self, object, event) -> bool:
        """
        Filter events
        """
        # not handle if cell is not blank or moves not allowed
        if self.state > 0 or not self.enabled:
            return False

        # mouse enter
        if event.type() == QEvent.Enter:
            self.setStyleSheet(f"""
                border: 3px solid cornflowerblue;
                border-radius: {CELL_RADIUS}px;
                background: darkred;
            """)
            return True

        # mouse leave
        if event.type() == QEvent.Leave:
            self.setStyleSheet(f"""
                border: 3px solid darkred;
                border-radius: {CELL_RADIUS}px;
                background: darkred;
            """)
            return True

        # mouse press
        if event.type() == QEvent.MouseButtonPress:
            self.pressed()
            return True

        return False
    
    def getState(self) -> int:
        """
        Get the state of the cell
        
        Return:
        - 0: empty
        - 1: black
        - 2: white
        """
        return self.state
    
    def hook(self, getTurnFunction):
        """
        Hook to other functions to get game status
        """
        self.pGetTurn = getTurnFunction

    def tempState(self, state: int):
        """
        Temporarily set state for preview
        """
        self.setStyleSheet(f"""
            border: 3px solid darkred;
            border-radius: {CELL_RADIUS}px;
            background: {colorFromIndex(state)};
        """)
    
    def setState(self, state: int):
        """
        Permanently set state
        """
        self.state = state
        self.tempState(state)
    
    def changeIndex(self, newIndex):
        self.index = newIndex
    
    def setEnable(self):
        self.enabled = True
    
    def setDisable(self):
        self.enabled = False


class QuarterWidget(MyWidget):
    """
    Class to simulate a quarter
    """
    
    def __init__(self, index: int, parent=None):
        """
        Constructor
        """
        super().__init__(parent)

        # create cells
        self.setLayout(QGridLayout(self))
        self.cells = [CellWidget(self, i) for i in range(9)]
        for i in range(3):
            for j in range(3):
                self.layout().addWidget(self.cells[i * 3 + j], i, j)
        
        # set look
        self.setStyleSheet("""
            border: 3px solid white;
            border-radius: 10px;
            background: firebrick;
        """)
        self.setFixedSize(QUARTER_SIZE, QUARTER_SIZE)
        
        # set properties
        self.index = index
    
    def rotate(self, swapList):
        """
        Rotate the quarter

        Args:
        - swapList: the list of positions for correct swapping
        """
        # Remove cells from the layout
        for i in range(9):
            self.layout().removeWidget(self.cells[i])
            self.cells[i].setParent(None)

        # Swap positions
        for i, j in swapList:
            self.cells[i], self.cells[j] = self.cells[j], self.cells[i]

        # add cells to the layout
        for i in range(3):
            for j in range(3):
                # update new index
                self.cells[i * 3 + j].changeIndex(i * 3 + j)
                # re-add to layout
                self.layout().addWidget(self.cells[i * 3 + j], i, j)
                self.cells[i].setParent(self)
    
    def getState(self) -> int:
        """
        Get current state of the quarter
        """
        ret = 0
        for i in range(9):
            ret += POW_CELLS[i] * self.cells[i].getState()
        return ret
    
    def tempState(self, state):
        """
        Temporarily set state for preview
        """
        for i in range(9):
            self.cells[i].tempState(getDigit(state, i, POW_CELLS))
    
    def setState(self, state):
        """
        Permanently set state
        """
        for i in range(9):
            self.cells[i].setState(getDigit(state, i, POW_CELLS))
    
    def setEnable(self):
        for i in range(9):
            self.cells[i].setEnable()
    
    def setDisable(self):
        for i in range(9):
            self.cells[i].setDisable()


class BoardWidget(MyWidget):
    """
    Class to simulate a board
    """

    # signals
    finishMove = pyqtSignal()

    def __init__(self, parent=None) -> None:
        """
        Constructor

        Args:
        - parent: the parent widget
        """
        super().__init__(parent)

        # create layout
        self.setLayout(QGridLayout(self))

        # create quarters
        self.quarters = [QuarterWidget(i, self) for i in range(4)]
        # connect to cell signal
        for i in range(4):
            for j in range(9):
                self.quarters[i].cells[j].rotationPhase.connect(self.showRotateButtons)
        self.layout().addWidget(self.quarters[0], 1, 2)
        self.layout().addWidget(self.quarters[1], 1, 1)
        self.layout().addWidget(self.quarters[2], 2, 1)
        self.layout().addWidget(self.quarters[3], 2, 2)

        # create rotate buttons
        # cw - ccw
        self.rotateButtons = [
            [QPushButton("v", self), QPushButton("<", self)],
            [QPushButton(">", self), QPushButton("v", self)],
            [QPushButton("^", self), QPushButton(">", self)],
            [QPushButton("<", self), QPushButton("^", self)]
        ]
        # add to layout
        buttonPositions = [
            [(1, 3), (0, 2)],
            [(0, 1), (1, 0)],
            [(2, 0), (3, 1)],
            [(3, 2), (2, 3)]
        ]
        for i in range(len(self.rotateButtons)):
            for j in range(len(self.rotateButtons[i])):
                # set sizes
                self.rotateButtons[i][j].setFixedSize(ROTATE_BUTTONS_SIZE, ROTATE_BUTTONS_SIZE)
                # add to layout
                self.layout().addWidget(self.rotateButtons[i][j], buttonPositions[i][j][0], buttonPositions[i][j][1], Qt.AlignCenter)
                # hide initially
                self.rotateButtons[i][j].hide()
        # connect to signal
        self.rotateButtons[0][0].clicked.connect(lambda: self.rotateButtonsPressed(0, 0))
        self.rotateButtons[0][1].clicked.connect(lambda: self.rotateButtonsPressed(0, 1))
        self.rotateButtons[1][0].clicked.connect(lambda: self.rotateButtonsPressed(1, 0))
        self.rotateButtons[1][1].clicked.connect(lambda: self.rotateButtonsPressed(1, 1))
        self.rotateButtons[2][0].clicked.connect(lambda: self.rotateButtonsPressed(2, 0))
        self.rotateButtons[2][1].clicked.connect(lambda: self.rotateButtonsPressed(2, 1))
        self.rotateButtons[3][0].clicked.connect(lambda: self.rotateButtonsPressed(3, 0))
        self.rotateButtons[3][1].clicked.connect(lambda: self.rotateButtonsPressed(3, 1))
        
        # set look
        self.setFixedSize(BOARD_SIZE_0, BOARD_SIZE_0)
    
    def getState(self) -> int:
        ret = 0;
        for i in range(4):
            ret += POW_QUARTERS[i] * self.quarters[i].getState()
        return ret
    
    def tempState(self, state: int):
        """
        Temporarily set state
        """
        for i in range(4):
            self.quarters[i].tempState(getDigit(state, i, POW_QUARTERS))
    
    def setState(self, state: int):
        """
        Permanently set state
        """
        for i in range(4):
            self.quarters[i].setState(getDigit(state, i, POW_QUARTERS))
    
    @pyqtSlot()
    def showRotateButtons(self):
        """
        Show rotate buttons
        """
        self.setFixedSize(BOARD_SIZE_1, BOARD_SIZE_1)
        for i1, i2 in self.rotateButtons:
            i1.show()
            i2.show()
        # not allow to add new piece
        self.setDisable()
    
    def rotateButtonsPressed(self, i, j):
        """
        Rotate buttons' pressed event
        """
        # rotate
        self.quarters[i].rotate(ROTATE_CCW if j > 0 else ROTATE_CW)
        # end rotation
        self.setFixedSize(BOARD_SIZE_0, BOARD_SIZE_0)
        for i1, i2 in self.rotateButtons:
            i1.hide()
            i2.hide()
        # allow to add new piece
        self.setEnable()
        # emit signal
        self.finishMove.emit()
    
    def hookTurn(self, pGetTurn):
        for i in range(4):
            for j in range(9):
                self.quarters[i].cells[j].hook(pGetTurn)
    
    def setEnable(self):
        for i in range(4):
            self.quarters[i].setEnable()
    
    def setDisable(self):
        for i in range(4):
            self.quarters[i].setDisable()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    wnd = BoardWidget()
    wnd.show()
    sys.exit(app.exec_())