"""
Imports the Python libraries needed to the project.
"""
import sys
from enum import Enum
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QGridLayout, QAction, QGroupBox, QRadioButton, QSlider, \
    QLabel, QPushButton, QApplication, QFileDialog, QColorDialog, QMessageBox
from PyQt5.QtGui import QIcon, QImage, QPen, QPainter, QColor
from PyQt5.QtCore import Qt, QPoint, QSize
from qtpy import QtCore, QtGui

"""
Defines an enum which represents the drawing modes.
"""
class DrawMode(Enum):
    Point = 1
    Line = 2


"""
Class inherited from a QWidget which initializes the toolbox on the left of the application.
"""
class ToolBox(QWidget):
    def __init__(self):
        super().__init__()

        """
        Sets a fix width so the toolbox doesn't get too thin or too large.
        """
        self.setMaximumWidth(150)
        self.setMinimumWidth(150)

        """
        Sets a vertical box layout as the default layout.
        """
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)


"""
Class inherited from a QWidget which represents our drawing area. 
"""
class DrawingArea(QWidget):
    def __init__(self):
        super().__init__()

        """
        Initializes two images which will be used later to resize or undo.
        """
        self.resizeSavedImage = QImage(0, 0, QImage.Format_RGB32)
        self.savedImage = QImage(0, 0, QImage.Format_RGB32)

        """
        Sets our default image with the right size filled in white.
        """
        self.image = QImage(self.width(), self.height(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        """
        Sets the draw default settings, such as the brush size, the color or the style.
        """
        self.drawing = False
        self.brushSize = 1
        self.brushColor = Qt.black
        self.brushStyle = Qt.SolidLine
        self.brushCap = Qt.RoundCap
        self.brushJoin = Qt.RoundJoin
        self.drawMode = DrawMode.Point

        """
        Initializes a point that we'll use later to draw lines.
        Sets a minimum width so the image width is never equal to 0. 
        """
        self.lastPoint = QPoint()
        self.setMinimumWidth(150)


    """
    Method called when the widget is resized.
    The image needs to be scaled with the new size or problems will occur.
    """
    def resizeEvent(self, event):
        self.image = self.image.scaled(self.width(), self.height())

    """
    Method called when a button of the mouse is pressed.
    Only the left click is interesting here.
    """
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            """
            If the draw mode is set to Point we draw at the position of the mouse.
            """
            if self.drawMode == DrawMode.Point:
                painter = QPainter(self.image)  # object which allows drawing to take place on an image
                painter.setPen(QPen(self.brushColor, self.brushSize, self.brushStyle, self.brushCap, self.brushJoin))
                painter.drawPoint(event.pos())
                self.drawing = True  # we are now entering draw mode
                self.lastPoint = event.pos()  # new point is saved as last point
            elif self.drawMode == DrawMode.Line:
                """
                Else if the draw mode is set to Line we save a first point and 
                draw a line when a second click is done.
                """
                if self.lastPoint == QPoint():
                    self.lastPoint = event.pos()
                else:
                    painter = QPainter(self.image)  # object which allows drawing to take place on an image
                    painter.setPen(QPen(self.brushColor, self.brushSize, self.brushStyle, self.brushCap, self.brushJoin))
                    painter.drawLine(self.lastPoint, event.pos())
                    self.lastPoint = QPoint()

            """
            Tells the library to update the widget, as something might have been drawn.
            """
            self.update()

    """
    Method called when the mouse is moved.
    Here it is only used when the draw mode is set to Point and if the user
    keeps drawing while moving the mouse.
    """
    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing & (self.drawMode == DrawMode.Point):
            painter = QPainter(self.image)  # object which allows drawing to take place on an image
            # allows the selection of brush colour, brush size, line type, cap type, join type
            painter.setPen(QPen(self.brushColor, self.brushSize, self.brushStyle, self.brushCap, self.brushJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    """
    Method called when a button of the mouse is released.
    Here again we only are interested about the left click.
    """
    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            """
            Saves the image before the modification.
            """
            self.savedImage = self.resizeSavedImage
            self.resizeSavedImage = self.image
            self.drawing = False

    """
    Method called when a painting event occurs.
    """
    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())


"""
Main class inherited from a QMainWindow which is the main window of the program.
"""
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        """
        Sets some default settings of the window such as the name, the size and the icon.
        """
        self.setWindowTitle("QPaint")
        self.setGeometry(100, 100, 800, 600)  # top, left, width, height
        self.setWindowIcon(QIcon("./icons/paint-brush.png"))

        """
        Initializes layouts and call the methods that will initialize 
        specific parts of the window.
        """
        self.grid = QGridLayout()
        self.box = ToolBox()
        self.imageArea = DrawingArea()
        self.setBrushSlider()
        self.setBrushStyle()
        self.setBrushCap()
        self.setBrushJoin()
        self.setColorChanger()

        """
        Creates a grid with the toolbox and the drawing area,
        which we both set in a widget which is the central widget of our window.
        """
        self.grid.addWidget(self.box, 0, 0, 1, 1)
        self.grid.addWidget(self.imageArea, 0, 1, 1, 6)
        win = QWidget()
        win.setLayout(self.grid)
        self.setCentralWidget(win)

        """
        Creates the menu bar of our window with 3 menus.
        """
        # menus
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu(" File")  # the space is required as "File" is reserved in Mac
        drawMenu = mainMenu.addMenu("Draw")
        helpMenu = mainMenu.addMenu("Help")

        """
        Creates the Save action and adds it to the "File" menu.
        """
        saveAction = QAction(QIcon("./icons/save.png"), "Save", self)
        saveAction.setShortcut("Ctrl+S")
        fileMenu.addAction(saveAction)
        """
        When the menu option is selected or the shortcut is used the save action is triggered.
        """
        saveAction.triggered.connect(self.save)

        """
        Creates the Open action and adds it to the "File" menu.
        """
        openAction = QAction(QIcon("./icons/open.png"), "Open", self)
        openAction.setShortcut("Ctrl+O")
        fileMenu.addAction(openAction)
        """
        When the menu option is selected or the shortcut is used the open action is triggered.
        """
        openAction.triggered.connect(self.open)

        """
        Creates the Undo action and adds it to the "File" menu.
        """
        undoAction = QAction(QIcon("./icons/undo.png"), "Undo", self)
        undoAction.setShortcut("Ctrl+Z")
        fileMenu.addAction(undoAction)
        """
        When the menu option is selected or the shortcut is used the undo action is triggered.
        """
        undoAction.triggered.connect(self.undo)

        """
        Creates the Clear action and adds it to the "File" menu.
        """
        clearAction = QAction(QIcon("./icons/clear.png"), "Clear", self)
        clearAction.setShortcut("Ctrl+C")
        fileMenu.addAction(clearAction)
        """
        When the menu option is selected or the shortcut is used the clear action is triggered.
        """
        clearAction.triggered.connect(self.clear)

        """
        Creates the Exit action and adds it to the "File" menu.
        """
        exitAction = QAction(QIcon("./icons/exit.png"), "Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        fileMenu.addAction(exitAction)
        """
        When the menu option is selected or the shortcut is used the exit action is triggered.
        """
        exitAction.triggered.connect(self.exitProgram)

        """
        Creates the Point action and adds it to the "Draw" menu.
        """
        self.pointAction = QAction("Point", self, checkable=True)
        self.pointAction.setShortcut("Ctrl+P")
        self.pointAction.setChecked(True)
        drawMenu.addAction(self.pointAction)
        """
        When the menu option is selected or the shortcut is used the change draw mode action is triggered.
        """
        self.pointAction.triggered.connect(lambda: self.changeDrawMode(self.pointAction))

        """
        Creates the Line action and adds it to the "Draw" menu.
        """
        self.lineAction = QAction("Line", self, checkable=True)
        self.lineAction.setShortcut("Ctrl+L")
        drawMenu.addAction(self.lineAction)
        """
        When the menu option is selected or the shortcut is used the change draw mode action is triggered.
        """
        self.lineAction.triggered.connect(lambda: self.changeDrawMode(self.lineAction))

        """
        Creates the About action and adds it to the "Help" menu.
        """
        aboutAction = QAction(QIcon("./icons/about.png"), "About", self)
        aboutAction.setShortcut("Ctrl+I")
        helpMenu.addAction(aboutAction)
        """
        When the menu option is selected or the shortcut is used the about action is triggered.
        """
        aboutAction.triggered.connect(self.about)

        """
        Creates the Help action and adds it to the "Help" menu.
        """
        helpAction = QAction(QIcon("./icons/help.png"), "Help", self)
        helpAction.setShortcut("Ctrl+H")
        helpMenu.addAction(helpAction)
        """
        When the menu option is selected or the shortcut is used the help action is triggered.
        """
        helpAction.triggered.connect(self.help)

        """
        Updates the widget with the default settings.
        """
        self.imageArea.update()

    """
    Method which changes the draw mode depending on which action has been called.
    """
    def changeDrawMode(self, check):
        if check.text() == "Point":
            self.pointAction.setChecked(True)
            self.lineAction.setChecked(False)
            self.imageArea.drawMode = DrawMode.Point
        elif check.text() == "Line":
            self.pointAction.setChecked(False)
            self.lineAction.setChecked(True)
            self.imageArea.drawMode = DrawMode.Line
        """
        Resets the saved point.
        """
        self.imageArea.lastPoint = QPoint()

    """
    Initializes the layout on which we can change the Join setting of the brush.
    """
    def setBrushJoin(self):
        self.brush_join_type = QGroupBox("Brush join")
        self.brush_join_type.setMaximumHeight(100)

        """
        Creates the radio buttons to let us make a choice between these 3 options.
        Each one is connected to a method which will change the setting depending on which
        button is clicked.
        """
        self.joinBtn1 = QRadioButton("Round")
        self.joinBtn1.clicked.connect(lambda: self.changeBrushJoin(self.joinBtn1))
        self.joinBtn2 = QRadioButton("Miter")
        self.joinBtn2.clicked.connect(lambda: self.changeBrushJoin(self.joinBtn2))
        self.joinBtn3 = QRadioButton("Bevel")
        self.joinBtn3.clicked.connect(lambda: self.changeBrushJoin(self.joinBtn3))

        """
        Sets a default value.
        Adds the buttons to the layout which is added to the parent box.
        """
        self.joinBtn1.setChecked(True)
        qv = QVBoxLayout()
        qv.addWidget(self.joinBtn1)
        qv.addWidget(self.joinBtn2)
        qv.addWidget(self.joinBtn3)
        self.brush_join_type.setLayout(qv)
        self.box.vbox.addWidget(self.brush_join_type)

    """
    Initializes the layout on which we can change the Type setting of the brush.
    """
    def setBrushStyle(self):
        self.brush_line_type = QGroupBox("Brush style")
        self.brush_line_type.setMaximumHeight(100)

        """
        Creates the radio buttons to let us make a choice between these 3 options.
        Each one is connected to a method which will change the setting depending on which
        button is clicked.
        """
        self.styleBtn1 = QRadioButton(" Solid")
        self.styleBtn1.setIcon(QIcon("./icons/solid.png"))
        self.styleBtn1.setIconSize(QSize(32, 64))
        self.styleBtn1.clicked.connect(lambda: self.changeBrushStyle(self.styleBtn1))

        self.styleBtn2 = QRadioButton(" Dash")
        self.styleBtn2.setIcon(QIcon("./icons/dash.png"))
        self.styleBtn2.setIconSize(QSize(32, 64))
        self.styleBtn2.clicked.connect(lambda: self.changeBrushStyle(self.styleBtn2))

        self.styleBtn3 = QRadioButton(" Dot")
        self.styleBtn3.setIcon(QIcon("./icons/dot.png"))
        self.styleBtn3.setIconSize(QSize(32, 64))
        self.styleBtn3.clicked.connect(lambda: self.changeBrushStyle(self.styleBtn3))

        """
        Sets a default value.
        Adds the buttons to the layout which is added to the parent box.
        """
        self.styleBtn1.setChecked(True)
        qv = QVBoxLayout()
        qv.addWidget(self.styleBtn1)
        qv.addWidget(self.styleBtn2)
        qv.addWidget(self.styleBtn3)
        self.brush_line_type.setLayout(qv)
        self.box.vbox.addWidget(self.brush_line_type)

    """
    Initializes the layout on which we can change the Cap setting of the brush.
    """
    def setBrushCap(self):
        self.brush_cap_type = QGroupBox("Brush cap")
        self.brush_cap_type.setMaximumHeight(100)

        """
        Creates the radio buttons to let us make a choice between these 3 options.
        Each one is connected to a method which will change the setting depending on which
        button is clicked.
        """
        self.capBtn1 = QRadioButton("Square")
        self.capBtn1.clicked.connect(lambda: self.changeBrushCap(self.capBtn1))
        self.capBtn2 = QRadioButton("Flat")
        self.capBtn2.clicked.connect(lambda: self.changeBrushCap(self.capBtn2))
        self.capBtn3 = QRadioButton("Round")
        self.capBtn3.clicked.connect(lambda: self.changeBrushCap(self.capBtn3))

        """
        Sets a default value.
        Adds the buttons to the layout which is added to the parent box.
        """
        self.capBtn3.setChecked(True)
        qv = QVBoxLayout()
        qv.addWidget(self.capBtn1)
        qv.addWidget(self.capBtn2)
        qv.addWidget(self.capBtn3)
        self.brush_cap_type.setLayout(qv)
        self.box.vbox.addWidget(self.brush_cap_type)

    """
    Method which changes the Join setting of the brush depending
    on which button has been previously clicked.
    """
    def changeBrushJoin(self, btn):
        if btn.text() == "Round":
            if btn.isChecked():
                self.imageArea.brushJoin = Qt.RoundJoin
        if btn.text() == "Miter":
            if btn.isChecked():
                self.imageArea.brushJoin = Qt.MiterJoin
        if btn.text() == "Bevel":
            if btn.isChecked():
                self.imageArea.brushJoin = Qt.BevelJoin

    """
    Method which changes the Cap setting of the brush depending
    on which button has been previously clicked.
    """
    def changeBrushCap(self, btn):
        if btn.text() == "Square":
            if btn.isChecked():
                self.imageArea.brushCap = Qt.SquareCap
        if btn.text() == "Flat":
            if btn.isChecked():
                self.imageArea.brushCap = Qt.FlatCap
        if btn.text() == "Round":
            if btn.isChecked():
                self.imageArea.brushCap = Qt.RoundCap

    """
    Method which changes the Type setting of the brush depending
    on which button has been previously clicked.
    """
    def changeBrushStyle(self, btn):
        if btn.text() == " Solid":
            if btn.isChecked():
                self.imageArea.brushStyle = Qt.SolidLine
        if btn.text() == " Dash":
            if btn.isChecked():
                self.imageArea.brushStyle = Qt.DashLine
        if btn.text() == " Dot":
            if btn.isChecked():
                self.imageArea.brushStyle = Qt.DotLine

    """
    Initializes the layout on which we can change the brush size.
    """
    def setBrushSlider(self):
        self.groupBoxSlider = QGroupBox("Brush size")
        self.groupBoxSlider.setMaximumHeight(100)

        """
        Sets a vertical slider with a min and a max value.
        """
        self.brush_thickness = QSlider(Qt.Horizontal)
        self.brush_thickness.setMinimum(1)
        self.brush_thickness.setMaximum(40)
        self.brush_thickness.valueChanged.connect(self.sizeSliderChange)

        """
        Sets a label to display the size of the brush.
        """
        self.brushSizeLabel = QLabel()
        self.brushSizeLabel.setText("%s px" % self.imageArea.brushSize)

        """
        Adds the buttons to the layout which is added to the parent box.
        """
        qv = QVBoxLayout()
        qv.addWidget(self.brush_thickness)
        qv.addWidget(self.brushSizeLabel)
        self.groupBoxSlider.setLayout(qv)

        self.box.vbox.addWidget(self.groupBoxSlider)

    """
    Method which changes the brush size depending on the value 
    sent from the slider. 
    """
    def sizeSliderChange(self, value):
        self.imageArea.brushSize = value
        self.brushSizeLabel.setText("%s px" % value)

    """
    Initializes the layout on which we can change the color of the brush.
    """
    def setColorChanger(self):
        self.groupBoxColor = QGroupBox("Color")
        self.groupBoxColor.setMaximumHeight(100)

        """
        Initializes a color and sets a button with this color as background.
        """
        self.col = QColor(0, 0, 0)
        self.brush_colour = QPushButton()
        self.brush_colour.setFixedSize(60, 60)
        self.brush_colour.clicked.connect(self.showColorDialog)
        self.brush_colour.setStyleSheet("background-color: %s" % self.col.name())
        self.box.vbox.addWidget(self.brush_colour)

        """
        Adds the buttons to the layout which is added to the parent box.
        """
        qv = QVBoxLayout()
        qv.addWidget(self.brush_colour)
        self.groupBoxColor.setLayout(qv)

        self.box.vbox.addWidget(self.groupBoxColor)

    """
    Method which displays a color picker and sets the brush color.
    """
    def showColorDialog(self):
        self.col = QColorDialog.getColor()
        if self.col.isValid():
            self.brush_colour.setStyleSheet("background-color: %s" % self.col.name())
            self.imageArea.brushColor = self.col

    """
    Method called when the main window is resized.
    Scales the image area with the new size.
    """
    def resizeEvent(self, a0: QtGui.QResizeEvent):
        if self.imageArea.resizeSavedImage.width() != 0:
            self.imageArea.image = self.imageArea.resizeSavedImage.scaled(self.imageArea.width(), self.imageArea.height(), QtCore.Qt.IgnoreAspectRatio)
        self.imageArea.update()

    """
    Method called when we execute the save action.
    It opens a file dialog in which the user can choose the path of where
    he would like to save the current image.
    """
    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":
            return
        self.imageArea.image.save(filePath)

    """
    Method called when we execute the open action.
    It opens a file dialog in which the user can choose the path of the image
    he wants to open in the program.
    """
    def open(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":
            return
        with open(filePath, 'rb') as f:
            content = f.read()

        """
        Loads the data from the file to the image.
        Scales it and updates the drawing area.
        """
        self.imageArea.image.loadFromData(content)
        self.imageArea.image = self.imageArea.image.scaled(self.imageArea.width(), self.imageArea.height(), QtCore.Qt.IgnoreAspectRatio)
        self.imageArea.resizeSavedImage = self.imageArea.image  # saves the image for later resizing
        self.imageArea.update()

    """
    Method called when we execute the undo action.
    The user can go back to the previous state of the image
    before the last modification he made.
    """
    def undo(self):
        copyImage = self.imageArea.image
        if self.imageArea.savedImage.width() != 0:
            """
            If the saved image exists, we set the actual image to the saved one scaled to the right size.
            """
            self.imageArea.image = self.imageArea.savedImage.scaled(self.imageArea.width(), self.imageArea.height(), QtCore.Qt.IgnoreAspectRatio)
        else:
            """
            If no saved image exist we just clean the current one.
            """
            self.imageArea.image = QImage(self.imageArea.width(), self.imageArea.height(), QImage.Format_RGB32)
            self.imageArea.image.fill(Qt.white)
        """
        Sets the saved image as the copy from the screen.
        """
        self.imageArea.savedImage = copyImage
        self.imageArea.update()

    """
    Method called when we execute the clear action.
    It fills the image in white and updates it.
    """
    def clear(self):
        self.imageArea.image.fill(Qt.white)
        self.imageArea.update()

    """
    Method called when we execute the exit action.
    Exits the program.
    """
    def exitProgram(self):
        QtCore.QCoreApplication.quit()

    """
    Method called when we execute the about action.
    Displays a message about the program.
    """
    def about(self):
        QMessageBox.about(self, "About QPaint",
                          "<p>This Qt Application is a basic paint program made with PyQt. "
                          "You can draw something by yourself and then save it as a file. "
                          "PNG and JPG files can also be opened and edited.</p>")

    """
    Method called when we execute the help action.
    Displays a help message about the program.
    """
    def help(self):
        msg = QMessageBox()
        msg.setText("Help"
                    "<p>Welcome on QPaint.</p> "
                    "<p>On the left side of the screen you can see a toolbox on which you have different boxes. "
                    "Each of these boxes contains buttons or sliders which allow you to customize the brush you want to"
                    "draw with.</p>"
                    "<p>The right size of the screen is the drawing area, where you can draw.</p> "
                    "<p>The program also has different menus you can see at the top of the window. "
                    "<p>These menus allow you to open a file, save your image, clean it, or even exit the program.</p>"
                    "We hope you will enjoy your experience."
                    "If you encounter any difficulty or need any information "
                    "you can send an email to nicolas.guillon@epitech.eu.</p>")
        msg.setWindowTitle("Help")
        msg.move(self.width() / 2, self.height() / 2)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    """
    Starts a new instance of the main window.
    """
    window = Window()
    window.show()
    app.exec()