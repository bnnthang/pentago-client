from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from boardwidget import MyWidget
from gamewindow import GameWindow
import playlocal
import playonline


class LauncherWindow(QMainWindow):
    """
    Launcher class
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super().__init__()

        # create central widget and layout
        self.setCentralWidget(MyWidget())
        self.centralWidget().setLayout(QVBoxLayout())

        self.setWindowTitle("Home")
        self.setObjectName("mainwnd")
        self.setStyleSheet("""
            #mainwnd {
                background: saddlebrown;
            }

            QPushButton#modebutton {
                color: white;
                border: 3px solid white;
                border-radius: 10px;
                background: firebrick;
            }

            QPushButton#modebutton:hover {
                background: darkred;
            }
        """)
        self.setFixedSize(500, 456)
        self.setWindowIcon(QIcon("img/tic-tac-toe.png"))

        modes = [
            QPushButton("Player vs Player (local)", self.centralWidget()),
            QPushButton("Player vs Bot (Player first)", self.centralWidget()),
            QPushButton("Player vs Bot (Bot first)", self.centralWidget()),
            QPushButton("Player vs Player (online)", self.centralWidget()),
            QPushButton("Instructions", self.centralWidget()),
            QPushButton("Credit", self.centralWidget())
        ]

        # self.centralWidget().layout().setAlignment()
        titleLabel = QLabel("PENTAGO")
        titleLabel.setStyleSheet("""
            font-size: 32px;
            color: white;
        """)
        titleLabel.setFixedHeight(100)
        self.centralWidget().layout().addWidget(titleLabel)
        self.centralWidget().layout().setAlignment(titleLabel, Qt.AlignCenter)
        for button in modes:
            # set look for button
            button.setFixedSize(300, 45)
            button.setObjectName("modebutton")
            self.centralWidget().layout().addWidget(button)
            self.centralWidget().layout().setAlignment(button, Qt.AlignHCenter)

        modes[0].clicked.connect(self.pvpClicked)
        modes[1].clicked.connect(self.pvbClicked)
        modes[2].clicked.connect(self.bvpClicked)
        modes[3].clicked.connect(self.pvpoClicked)
        modes[4].clicked.connect(self.instructionClicked)
        modes[5].clicked.connect(self.creditClicked)

    def pvpClicked(self):
        self.gamewnd = GameWindow("Black", "White")
        self.gamewnd.closing.connect(self.show)
        self.gamewnd.show()
        self.hide()

    def pvbClicked(self):
        self.gamewnd = playlocal.GameWithBot("Black", "White", True)
        self.gamewnd.closing.connect(self.show)
        self.gamewnd.show()
        self.hide()

    def bvpClicked(self):
        self.gamewnd = playlocal.GameWithBot("Black", "White")
        self.gamewnd.closing.connect(self.show)
        self.gamewnd.show()
        self.hide()

    def pvpoClicked(self):
        self.gamewnd = playonline.GameOnline("Black", "White")
        self.gamewnd.closing.connect(self.show)
        self.gamewnd.show()
        self.gamewnd.initConnection()
        self.hide()
    
    def instructionClicked(self):
        import webbrowser
        webbrowser.open_new_tab("https://entertainment.howstuffworks.com/leisure/brain-games/pentago2.htm")
    
    def creditClicked(self):
        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("Credit")
        msgBox.setInformativeText("This program was his course project for 15-112 at CMU Qatar in Fall 2020.")
        msgBox.setText("Thang Bui wrote this in Python.")
        msgBox.exec()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    wnd = LauncherWindow()
    wnd.show()
    sys.exit(app.exec_())