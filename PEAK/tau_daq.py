import DA30
import peak
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLineEdit, QLabel, QVBoxLayout, QMenu, QHBoxLayout
import matplotlib as plt
plt.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import sys

class SpectrumCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(SpectrumCanvas, self).__init__(fig)

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

        # get specturm button
        self.get_spectrum = QPushButton("get spectrum")
        self.get_spectrum
        self.get_spectrum.clicked.connect(self.scan_spectrum)

        # test data button
        self.test_spectrum = QPushButton("test data")
        self.test_spectrum
        self.test_spectrum.clicked.connect(self.test_data)

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
        self.layout.addWidget(self.get_spectrum)
        self.layout.addWidget(self.test_spectrum)
        self.layout.addLayout(self.configuration)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)

    def do_sweep(self, checked):
        print(f"sweeping: {checked}")
        print(self.KE_input.text())
        print(self.DT_input.text())
        print(self.points_input.text())
    
    def scan_spectrum(self):
        seq_loq_id = 'test'
        acq_log_id = 'test'
        self.analyser.start_measurement(seq_loq_id, acq_log_id)

        configuration_name = self.analyser.configuration_name
        spectrum_definition = {
                        'ElementSetName': configuration_name,
                        'Name': 'DA30_Test',
                        'LensModeName': 'DA30_01',
                        'PassEnergy': 10,
                        'FixedAxes': {'X': {'Center': 50.0}, 'Z' : {'Center': 5.0}},
                        'AcquisitionMode' : 'Image', 
                        'DwellTime' : 1.0, 
                        'StoreSpectrum': False,
                        'StoreAcquisitionData': False,
                        }    

        spectrum_id = self.analyser.define_spectrum(spectrum_definition)
        self.analyser.setup_spectrum(spectrum_id)
        self.analyser.acquire(spectrum_id)

        spectrum = self.analyser.get_measured_spectrum(spectrum_id)
        self.analyser.finish_measurement()

    def test_data(self):
        print('testing data')
        base_dir = 'D:\git\TAU_ARPES\Spectrum_1'
        spectrum_id = '38eb55cb-c861-45ae-8103-20531210ae95'
        spectrum = peak.PeakSpectrum()
        spectrum.create_from_file(base_dir=base_dir, spectrum_id=spectrum_id)
        spectrum.show(data_type=peak.PeakSpectrumType.Count)

    
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