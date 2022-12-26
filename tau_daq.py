import PEAK.DA30 as DA30
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout
import matplotlib as plt
plt.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from StandaStage.standa_api import StandaStage, Standa
import sys

class SpectrumCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=4, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(SpectrumCanvas, self).__init__(fig)

class SweepCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=4, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(SweepCanvas, self).__init__(fig)

class DaqWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TAU ARPES DAQ")
        self.setFixedSize(QSize(1000, 1000))
        
        # connect to analyser button
        self.connect_analyser = QPushButton("connect analyser")
        self.connect_analyser.clicked.connect(self.connect_to_analyser)
        
        # connect to stage button
        self.connect_stage = QPushButton("connect stage")
        self.connect_stage.clicked.connect(self.connect_to_stage)

        # start sweep button
        self.start_sweep = QPushButton("start sweep")
        self.start_sweep.clicked.connect(self.do_sweep)

        # get stage position button
        self.stage_position = QPushButton("get stage position")
        self.stage_position.clicked.connect(self.get_stage_position)

        # get specturm button
        self.get_spectrum = QPushButton("get spectrum")
        self.get_spectrum.clicked.connect(self.scan_spectrum)

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
        
        # grouping configuration
        self.configuration.addLayout(self.kinetic_energy)
        self.configuration.addLayout(self.dwell_time)
        self.configuration.addLayout(self.points)
        
        # setting new t0
        self.set_t_0 = QHBoxLayout()
        self.new_t_0_label = QLabel('new t0 in fs')
        self.new_t_0_input = QLineEdit()
        self.set_new_t_0 = QPushButton('Ok')
        self.set_new_t_0.clicked.connect(self.set_new_t_0_value)

        self.set_t_0.addWidget(self.new_t_0_label)
        self.set_t_0.addWidget(self.new_t_0_input)
        self.set_t_0.addWidget(self.set_new_t_0)

        # spectrum
        self.spectrum = SpectrumCanvas()

        # sweep
        self.sweep_canvas = SweepCanvas()

        self.layout.addWidget(self.connect_analyser)
        self.layout.addWidget(self.connect_stage)
        self.layout.addWidget(self.stage_position)
        self.layout.addLayout(self.set_t_0)
        self.layout.addWidget(self.start_sweep)
        self.layout.addWidget(self.get_spectrum)
        self.layout.addLayout(self.configuration)
        self.layout.addWidget(self.spectrum)
        self.layout.addWidget(self.sweep_canvas)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)

    def do_sweep(self):
        if self.KE_input.text() == "" or self.DT_input == "":
            print('enter kinetic energy and dwell time values before sweep')
            return
        KE = float(self.KE_input.text())
        DT = float(self.DT_input.text())
        try:
            points = DaqWindow.get_sweep_points(self.points_input.text())
        except Exception as e:
            print('sweep points entered in a non-valid manner')
            print(e)
            return
        sweep = {}
        for point in points:
            self.stage.go_to_time_fs(point)
            spectrum = self.analyser.do_measurement(KE, DT)
            self.spectrum.axes.cla()
            spectrum.show_plane(self.spectrum.axes)
            self.spectrum.draw()
            sweep[point] = sum(sum(spectrum.raw_count_data))
            self.sweep_canvas.axes.plot([point for point in sweep], [sweep[point] for point in sweep])
            self.sweep_canvas.draw()


        
    def get_sweep_points(points_text):
        points = []
        for section in points_text.split(','):
            [start, stop, step] = section.split('_')
            print(f'{start} {stop} {step}')
            points += [x for x in range(int(start), int(stop), int(step))]
        return points
    
    def scan_spectrum(self):
        if self.KE_input.text() != "" and self.DT_input != "":
            spectrum = self.analyser.do_measurement(float(self.KE_input.text()), float(self.DT_input.text()))
        else:
            print('did not receive kinetic energy input and dwelling time input, defaulting to 1.75eV and 1.0s')
            spectrum = self.analyser.do_measurement()
        self.spectrum.axes.cla()
        spectrum.show_plane(self.spectrum.axes)
        self.spectrum.draw()
    
    def connect_to_analyser(self):
        try:
            self.analyser = DA30.DA30()
        except Exception as e:
            checked = False
            print(repr(e))
    
    def connect_to_stage(self):
        try:
            device_id = Standa.find_device()
            self.stage = StandaStage(device_id)
        except Exception as e:
            print(repr(e))
    
    def get_stage_position(self):
        print(self.stage.get_pos())

    def set_new_t_0_value(self):
        t_0 = int(self.new_t_0_input.text())
        self.stage.set_zero_pos_by_time(t_0)
        self.new_t_0_input.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DaqWindow()
    window.show()
    app.exec()