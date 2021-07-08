import sys
import os
import socket
from PyQt5 import QtGui
import cv2
from PyQt5 import QtCore, QtWidgets
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtWidgets import QLabel, QVBoxLayout
from PyQt5.uic.properties import QtGui
from numpy.core.records import ndarray

from numpy_socket import NumpySocket


class SocketWorker(QtCore.QObject):
    dataChanged = QtCore.pyqtSignal(ndarray)

    def __init__(self, parent=None):
        super(SocketWorker, self).__init__(parent)
        self.server_start = False

    @QtCore.pyqtSlot()
    def start(self):
        self.server_start = True
        self.sock_receiver = NumpySocket()
        ip = socket.gethostbyname(socket.gethostname())
        port = 515
        self.sock_receiver.initalize_receiver(ip, port)
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock.bind((ip, port))
        self.process()

    def process(self):
        while self.server_start:
            frame = self.sock_receiver.receive_array()
            self.dataChanged.emit(frame)


class VideoWidget(QtWidgets.QWidget):
    started = QtCore.pyqtSignal()

    def __init__(self, parent=None):

        super(VideoWidget, self).__init__(parent)
        self.setWindowTitle("Qt live label demo")
        self.display_width = 640
        self.display_height = 480
        btn = QtWidgets.QPushButton("Click Me")
        btn.clicked.connect(self.started)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(QtWidgets.QLabel(f"tcp receiver on local ip:{socket.gethostbyname(socket.gethostname())} port:515"))
        lay.addWidget(btn)
        # create the label that holds the image
        self.image_label = QLabel(self)
        # create a text label
        self.textLabel = QLabel('Demo')
        lay.addWidget(self.textLabel)
        lay.addWidget(self.image_label)
        grey = QPixmap(self.display_width, self.display_height)
        grey.fill(QColor('darkGray'))
        self.image_label.setPixmap(grey)

        self.setWindowTitle("udp receive")

    @QtCore.pyqtSlot(ndarray)
    def receive_frame(self, frame):
        print(frame)
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(frame)
        self.image_label.setPixmap(qt_img)
        # self.lst.insertItem(0, frame)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    print(socket.gethostbyname(socket.gethostname()))
    w = VideoWidget()
    worker = SocketWorker()
    thread = QtCore.QThread()
    thread.start()
    worker.moveToThread(thread)
    w.started.connect(worker.start)
    worker.dataChanged.connect(w.receive_frame)
    w.show()
    sys.exit(app.exec_())
