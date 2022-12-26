import DA30
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLineEdit, QLabel, QVBoxLayout, QMenu, QHBoxLayout

import sys

class DaqWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TAU ARPES DAQ")
        self.setFixedSize(QSize(600, 600))
        
        # connect to analyser buttton
        self.connect_analyser = QPushButton("connect")
        self.connect_analyser.setCheckable(True)
        self.connect_analyser.clicked.connect(self.connect_to_analyser)
        
        # start sweep button
        self.start_sweep = QPushButton("start sweep")
        self.start_sweep.setCheckable(True)
        self.start_sweep.clicked.connect(self.do_sweep)
        

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

        spectrum_definition = {
                    'ElementSetName': "configuration_name",
                    'Name': 'DA30_Test',
                    'LensModeName': 'DA30_01',
                    'PassEnergy': 10,
                    'FixedAxes': {'X': {'Center': 50.0}, 'Z' : {'Center': 5.0}},
                    'AcquisitionMode' : 'Image', 
                    'DwellTime' : 1.0, 
                    'StoreSpectrum': False,
                    'StoreAcquisitionData': False,
                     }
        
        # grouping configuration
        self.configuration.addLayout(self.kinetic_energy)
        self.configuration.addLayout(self.dwell_time)
        self.configuration.addLayout(self.points)
        
        self.layout.setSpacing(1)
        self.layout.addWidget(self.connect_analyser)
        self.layout.addWidget(self.start_sweep)
        self.layout.addLayout(self.configuration)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)

    def do_sweep(self, checked):
        print(f"sweeping: {checked}")
        print(self.KE_input.text())
        print(self.DT_input.text())
        print(self.points_input.text())
    
    def connect_to_analyser(self, checked):
        if checked:
            try:
                self.analyser = DA30.DA30()
            except Exception as e:
                checked = False
                print(repr(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DaqWindow()
    window.show()
    app.exec()