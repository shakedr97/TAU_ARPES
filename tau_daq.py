import enum
import PEAK.DA30 as DA30
from PyQt6.QtCore import QSize, QRunnable, QThreadPool, pyqtSlot
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap
import matplotlib as plt
plt.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from StandaStage.standa_api import StandaStage, Standa
import sys

window_height = 900
window_width = 1500

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

class ConnectAnalyser(QRunnable):
    def __init__(self, controls):
        QRunnable.__init__(self)
        self.controls = controls
    
    @pyqtSlot()
    def run(self):
        try:
            self.controls.connect_analyser_indicator.set_ongoing()
            self.controls.analyser = DA30.DA30()
            self.controls.connect_analyser_indicator.set_check()
        except Exception as e:
            self.controls.connect_analyser_indicator.set_fail()
            print(repr(e))

class ConnectStage(QRunnable):
    def __init__(self, controls):
        QRunnable.__init__(self)
        self.controls = controls
    
    @pyqtSlot()
    def run(self):
        try:
            self.controls.connect_stage_indicator.set_ongoing()
            device_id = Standa.find_device()
            self.controls.stage = StandaStage(device_id)
            self.controls.connect_stage_indicator.set_check()
        except Exception as e:
            self.controls.connect_stage_indicator.set_fail()
            print(repr(e))

class Indicator(QLabel):
    def __init__(self):
        QLabel.__init__(self)
        self.setFixedSize(QSize(50,50))
        self.ongoing = QPixmap('images\hourglass.png')
        self.ongoing = self.ongoing.scaledToHeight(70)
        self.ongoing = self.ongoing.scaledToWidth(70)
        self.check = QPixmap('images\check_mark.png')
        self.check = self.check.scaledToHeight(50)
        self.check = self.check.scaledToWidth(50)
        self.fail = QPixmap('images\\fail_mark.png')
        self.fail = self.fail.scaledToHeight(50)
        self.fail = self.fail.scaledToWidth(50)
    
    def set_ongoing(self):
        self.setPixmap(self.ongoing)
        self.show()
    
    def set_check(self):
        self.setPixmap(self.check)
        self.show()
    
    def set_fail(self):
        self.setPixmap(self.fail)
        self.show()

class AnalyserMission(enum.Enum):
    GET_SPECTRUM = 1
    SWEEP = 2

class AnalyserWorker(QRunnable):
    def __init__(self, controls, mission):
        QRunnable.__init__(self)
        self.controls: Controls = controls
        self.mission = mission
    
    @pyqtSlot()
    def run(self):
        # self.controls.sweep_spinner.startAnimation()
        if self.mission == AnalyserMission.GET_SPECTRUM:
            if self.controls.KE_input.text() != "" and self.controls.DT_input != "":
                KE = float(self.controls.KE_input.text())
                DT = float(self.controls.DT_input.text())
                self.controls.analyser.start_measurement(KE, DT)
            else:
                print('did not receive kinetic energy input and dwelling time input, defaulting to 1.75eV and 1.0s')
                self.controls.analyser.start_measurement()
            while not self.controls.stop:
                self.controls.spectrum.axes.cla()
                spectrum = self.controls.analyser.take_measurement()
                spectrum.show_plane(self.controls.spectrum.axes)
                self.controls.spectrum.draw()
            self.controls.analyser.stop_measurement()
        elif self.mission == AnalyserMission.SWEEP:
            if self.controls.KE_input.text() == "" or self.controls.DT_input.text() == "":
                print('enter kinetic energy and dwell time values before sweep')
                return
            KE = float(self.controls.KE_input.text())
            DT = float(self.controls.DT_input.text())
            try:
                points = Controls.get_sweep_points(self.controls.points_input.text())
            except Exception as e:
                print('sweep points entered in a non-valid manner')
                print(e)
                return
            sweep = {point : 0 for point in points}
            self.controls.analyser.start_measurement(KE, DT)
            count = 0
            try:
                while not self.controls.stop:
                    count += 1
                    for point in points:
                        print(point)
                        if self.controls.stop:
                            self.controls.analyser.stop_measurement()
                            return
                        QApplication.processEvents()
                        self.controls.stage.go_to_time_fs(point)
                        spectrum = self.controls.analyser.take_measurement()
                        self.controls.spectrum.axes.cla()
                        spectrum.show_plane(self.controls.spectrum.axes)
                        self.controls.spectrum.draw()
                        sweep[point] = (sweep[point] * (count - 1) + sum(sum(spectrum.raw_count_data))) / count
                        self.controls.sweep_canvas.axes.cla()
                        self.controls.sweep_canvas.axes.plot([point for point in sweep], [sweep[point] for point in sweep], marker='o')
                        self.controls.sweep_canvas.draw()
                    points.reverse()
            except Exception as e:
                print(e)
                self.controls.analyser.stop_measurement()
        # self.controls.sweep_spinner.stopAnimation()

class Controls(QWidget):
    def __init__(self, spectrum, sweep_canvas, threadpool):
        self.stage: StandaStage = None
        QWidget.__init__(self)
        self.setFixedSize(QSize(window_width // 3, window_height))
        self.spectrum = spectrum
        self.sweep_canvas = sweep_canvas
        self.threadpool = threadpool
        self.controls_layout = QVBoxLayout()

        # connect to analyser button
        self.connect_analyser = QHBoxLayout()
        self.connect_analyser_button = QPushButton("connect analyser")
        self.connect_analyser_button.clicked.connect(self.connect_to_analyser)
        self.connect_analyser_indicator = Indicator()
        self.connect_analyser.addWidget(self.connect_analyser_button)
        self.connect_analyser.addWidget(self.connect_analyser_indicator)
        
        # connect to stage button
        self.connect_stage = QPushButton("connect stage")
        
        self.connect_stage = QHBoxLayout()
        self.connect_stage_button = QPushButton("connect stage")
        self.connect_stage_button.clicked.connect(self.connect_to_stage)
        self.connect_stage_indicator = Indicator()
        self.connect_stage.addWidget(self.connect_stage_button)
        self.connect_stage.addWidget(self.connect_stage_indicator)

        # get stage position button
        self.stage_position = QHBoxLayout()
        self.stage_position_button = QPushButton("get stage position")
        self.stage_position_button.clicked.connect(self.get_stage_position)
        self.stage_position_output = QLabel()
        self.stage_position_output.setMaximumSize(QSize(100, 10))
        self.stage_position.addWidget(self.stage_position_button)
        self.stage_position.addWidget(self.stage_position_output)

        # start sweep button
        self.start_sweep = QHBoxLayout()
        self.start_sweep_button: QWidget = QPushButton("start sweep")
        self.start_sweep_button.clicked.connect(self.do_sweep)
        # self.sweep_spinner = Loading()
        self.start_sweep.addWidget(self.start_sweep_button)
        # self.start_sweep.addWidget(self.sweep_spinner)

        # stop sweep button
        self.stop_sweep = QPushButton('stop sweep')
        self.stop_sweep.clicked.connect(self.do_stop_sweep)

        # get specturm button
        self.get_spectrum = QPushButton("get spectrum")
        self.get_spectrum.clicked.connect(self.scan_spectrum)

         # sweep configuration
        self.configuration = QVBoxLayout()
        
        # kinetic energy
        self.kinetic_energy = QHBoxLayout()
        self.KE_label = QLabel('kinetic energy (eV)')
        self.KE_input = QLineEdit('1.5')
        self.kinetic_energy.addWidget(self.KE_label)
        self.kinetic_energy.addWidget(self.KE_input)

        # dwell time
        self.dwell_time = QHBoxLayout()
        self.DT_label = QLabel('dwell time (s)')
        self.DT_input = QLineEdit('1')
        self.dwell_time.addWidget(self.DT_label)
        self.dwell_time.addWidget(self.DT_input)

        # time points
        self.points = QHBoxLayout()
        self.points_label = QLabel('points: [start_1, stop_1, step_1],...')
        self.points_input = QLineEdit('-500_600_100')
        self.points.addWidget(self.points_label)
        self.points.addWidget(self.points_input)
        
        # grouping configuration
        self.configuration.addLayout(self.kinetic_energy)
        self.configuration.addLayout(self.dwell_time)
        self.configuration.addLayout(self.points)

        # set new stage position
        self.set_stage_pos = QHBoxLayout()
        self.set_stage_pos_label = QLabel('new stage position in mm')
        self.set_stage_pos_input = QLineEdit()
        self.set_stage_pos_button = QPushButton('Ok')
        self.set_stage_pos_button.clicked.connect(self.do_set_stage_position)
        self.set_stage_pos.addWidget(self.set_stage_pos_label)
        self.set_stage_pos.addWidget(self.set_stage_pos_input)
        self.set_stage_pos.addWidget(self.set_stage_pos_button)
        
        # setting new t0
        self.set_t_0 = QHBoxLayout()
        self.new_t_0_label = QLabel('new t0 in fs')
        self.new_t_0_input = QLineEdit()
        self.set_new_t_0 = QPushButton('Ok')
        self.set_new_t_0.clicked.connect(self.set_new_t_0_value)
        self.set_t_0.addWidget(self.new_t_0_label)
        self.set_t_0.addWidget(self.new_t_0_input)
        self.set_t_0.addWidget(self.set_new_t_0)

         # setting new t0 position
        self.set_t_0_position = QHBoxLayout()
        self.new_t_0_position_label = QLabel('new t0 in mm')
        self.new_t_0_input_position = QLineEdit()
        self.set_new_t_0_position = QPushButton('Ok')
        self.set_new_t_0_position.clicked.connect(self.set_new_t_0_value_position)
        self.set_t_0_position.addWidget(self.new_t_0_position_label)
        self.set_t_0_position.addWidget(self.new_t_0_input_position)
        self.set_t_0_position.addWidget(self.set_new_t_0_position)

        self.controls_layout.addLayout(self.connect_analyser)
        self.controls_layout.addLayout(self.connect_stage)
        self.controls_layout.addLayout(self.stage_position)
        self.controls_layout.addLayout(self.set_t_0)
        self.controls_layout.addLayout(self.set_t_0_position)
        self.controls_layout.addLayout(self.set_stage_pos)
        self.controls_layout.addLayout(self.start_sweep)
        self.controls_layout.addWidget(self.stop_sweep)
        self.controls_layout.addWidget(self.get_spectrum)
        self.controls_layout.addLayout(self.configuration)

        self.setLayout(self.controls_layout)

    def connect_to_analyser(self):
        worker = ConnectAnalyser(self)
        self.threadpool.start(worker)
    
    def connect_to_stage(self):
        worker = ConnectStage(self)
        self.threadpool.start(worker)
    
    def get_stage_position(self):
        self.stage_position_output.setText('{:10.4f}'.format(self.stage.get_pos_mm()))

    def set_new_t_0_value(self):
        t_0 = int(self.new_t_0_input.text())
        self.stage.set_zero_pos_by_time(t_0)
        self.new_t_0_input.clear()
    
    def set_new_t_0_value_position(self):
        position = float(self.new_t_0_input_position.text())
        self.stage.set_zero_pos_by_position(position)
        self.new_t_0_input_position.clear()

    def do_set_stage_position(self):
        position = float(self.set_stage_pos_input.text())
        self.stage.move_to_mm(position)

    def do_sweep(self):
        worker = AnalyserWorker(self, AnalyserMission.SWEEP)
        self.stop = False
        self.threadpool.start(worker)
    
    def do_stop_sweep(self):
        self.stop = True

    def get_sweep_points(points_text):
        points = []
        for section in points_text.split(','):
            [start, stop, step] = section.split('_')
            print(f'{start} {stop} {step}')
            points += [x for x in range(int(start), int(stop), int(step))]
        return points
    
    def scan_spectrum(self):
        worker = AnalyserWorker(self, AnalyserMission.GET_SPECTRUM)
        self.stop = False
        self.threadpool.start(worker)


class DaqWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.threadpool = QThreadPool()
        
        self.setWindowTitle("TAU ARPES DAQ")
        self.setFixedSize(QSize(window_width, window_height))

        self.layout = QHBoxLayout()
        self.results = QVBoxLayout()
        # spectrum
        self.spectrum = SpectrumCanvas()

        # sweep
        self.sweep_canvas = SweepCanvas()
        self.results.addWidget(self.spectrum)
        self.results.addWidget(self.sweep_canvas)

        self.controls = Controls(self.spectrum, self.sweep_canvas, self.threadpool)

        self.layout.addWidget(self.controls)
        self.layout.addLayout(self.results)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DaqWindow()
    window.show()
    app.exec()