from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLineEdit, QLabel, QVBoxLayout, QMenu, QHBoxLayout

import sys

class DaqWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TAU ARPES DAQ")
        self.setFixedSize(QSize(400, 300))
        self.button = QPushButton("start sweep")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.do_sweep)


        self.layout = QVBoxLayout()
        # sweep configuration
        self.configuration = QVBoxLayout()
        
        # kinetic energy
        self.kinetic_energy = QHBoxLayout()
        self.KE_label = QLabel('kinetic energy (eV)')
        self.KE_input = QLineEdit()
        self.kinetic_energy.addWidget(self.KE_label)
        self.kinetic_energy.addWidget(self.KE_input)

        # dwell time
        self.dwell_time = QHBoxLayout()
        self.DT_label = QLabel('dwell time (s)')
        self.DT_input = QLineEdit()
        self.dwell_time.addWidget(self.DT_label)
        self.dwell_time.addWidget(self.DT_input)

        # time points
        self.points = QHBoxLayout()
        self.points_label = QLabel('points: [start_1, stop_1, step_1],...')
        self.points_input = QLineEdit()
        self.points.addWidget(self.points_label)
        self.points.addWidget(self.points_input)
        

        self.layout.addWidget(self.button)
        self.configuration.addLayout(self.kinetic_energy)
        self.configuration.addLayout(self.dwell_time)
        self.configuration.addLayout(self.points)
        self.layout.addLayout(self.configuration)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)

    def do_sweep(self, checked):
        print(f"sweeping: {checked}")
        print(self.KE_input.text())
        print(self.DT_input.text())
        print(self.points_input.text())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DaqWindow()
    window.show()
    app.exec()