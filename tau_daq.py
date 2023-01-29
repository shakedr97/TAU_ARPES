import sys
from StandaStage.standa_api import StandaStage, Standa
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import enum
import PEAK.DA30 as DA30
from PyQt5.QtCore import QSize, QRunnable, QThreadPool, pyqtSlot
from PyQt5.QtCore import Qt as Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QComboBox
from PyQt5.QtGui import QPixmap
import matplotlib as plt

plt.use('Qt5Agg')

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
        self.setFixedSize(QSize(50, 50))
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

    def set_blank(self):
        self.hide()


class PointsSlider(QSlider):

    def __init__(self):
        QSlider.__init__(self, Qt.Orientation.Horizontal)

    def setPoints(self, points):
        self.points = {
            point: index
            for (point, index) in zip(points, range(len(points)))
        }
        self.setMinimum(0)
        self.setMaximum(len(points) - 1)

    def setPosition(self, point):
        self.setValue(self.points[point])


class AnalyserMission(enum.Enum):
    Aqcuire = 1
    Sweep = 2


class AnalyserWorker(QRunnable):

    def __init__(self, controls, mission, gui):
        QRunnable.__init__(self)
        self.controls: Controls = controls
        self.mission = mission
        self.gui: DaqWindow = gui

    @pyqtSlot()
    def run(self):
        if self.mission == AnalyserMission.Aqcuire:
            if self.controls.KE_input.text(
            ) != "" and self.controls.DT_input != "":
                KE = float(self.controls.KE_input.text())
                DT = float(self.controls.DT_input.text())
                PE = int(self.controls.PE_input.text())
                self.controls.analyser.start_measurement(KE, DT, PE)
            else:
                print(
                    'did not receive all params kinetic energy (float), dwell time (float), pass energy (int), no starting measurement'
                )
                return
            while not self.controls.stop:
                self.controls.spectrum.axes.cla()
                spectrum = self.controls.analyser.take_measurement()
                spectrum.show_plane(self.controls.spectrum.axes)
                self.controls.spectrum.draw()
            self.controls.analyser.stop_measurement()
        elif self.mission == AnalyserMission.Sweep:
            if self.controls.KE_input.text(
            ) == "" or self.controls.DT_input.text() == "":
                print(
                    'enter kinetic energy and dwell time values before sweep')
                return
            KE = float(self.controls.KE_input.text())
            DT = float(self.controls.DT_input.text())
            try:
                points = Controls.get_sweep_points(
                    self.controls.points_input.text())
            except Exception as e:
                print('sweep points entered in a non-valid manner')
                print(e)
                return
            self.controls.sweep_indicator.setPoints(points)
            self.controls.sweep_data = None  # FIXME: move sweep data out of controls
            self.controls.analyser.start_measurement(KE, DT)
            count = 0
            try:
                while not self.controls.stop:
                    count += 1
                    self.controls.current_sweep_value.setText(f'{count}')
                    if count % int(self.controls.save_interval_input.text()) == 0:
                        self.gui.do_export_spectrum()
                    for point in points:
                        self.controls.sweep_indicator.setPosition(point)
                        self.controls.sweep_point_indicator.setText(str(point))
                        print(point)
                        if self.controls.stop:
                            self.controls.analyser.stop_measurement()
                            return
                        QApplication.processEvents()
                        self.controls.stage.go_to_time_fs(point)
                        spectrum = self.controls.analyser.take_measurement()
                        if not self.controls.sweep_data:
                            self.controls.sweep_data = SweepData(
                                spectrum.xaxis, spectrum.yaxis)
                        if count > 1:
                            self.controls.sweep_data.sweep[point] = (
                                self.controls.sweep_data.sweep[point] * (count - 1) + spectrum.raw_count_data) / count
                        else:
                            self.controls.sweep_data.sweep[
                                point] = spectrum.raw_count_data
                        self.controls.spectrum.axes.cla()
                        self.controls.sweep_data.show_spectrum(
                            self.controls.spectrum.axes, point)
                        self.controls.spectrum.draw()
                        self.controls.sweep_canvas.axes.cla()
                        time = [
                            point for point in self.controls.sweep_data.sweep
                        ]
                        counts = [
                            sum(sum(self.controls.sweep_data.sweep[point]))
                            for point in self.controls.sweep_data.sweep
                        ]
                        self.controls.sweep_canvas.axes.plot(time,
                                                             counts,
                                                             marker='o')
                        self.controls.sweep_canvas.draw()
                    points.reverse()
            except Exception as e:
                print(e)
                self.controls.analyser.stop_measurement()


class SweepData:

    def __init__(self, xaxis, yaxis):
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.sweep = {}

    def show_spectrum(self, view, point):
        x_axis = self.xaxis
        y_axis = self.yaxis

        plane = self.sweep[point]

        x_min = x_axis["Offset"]
        x_max = x_min + x_axis["Delta"] * (x_axis["Count"] - 1)
        y_min = y_axis["Offset"]
        y_max = y_min + y_axis["Delta"] * (y_axis["Count"] - 1)
        view.imshow(
            plane,
            interpolation="nearest",
            extent=[x_min, x_max, y_min, y_max],
            aspect="auto",
            origin="lower",
        )
        view.set_xlabel(x_axis["Label"] + " [" + x_axis["Unit"] + "]")
        view.set_ylabel(y_axis["Label"] + " [" + y_axis["Unit"] + "]")

    def export(self, file_name, column_delimiter='\t', row_delimiter='\n'):
        with open(f'exports\\{file_name}.txt', 'w') as f:
            f.write(f'time{column_delimiter}counts{row_delimiter}')
            for point in self.sweep:
                f.write(
                    f'{point}{column_delimiter}{sum(sum(self.sweep[point]))}{row_delimiter}'
                )

    def export_raw(self, file_name, column_delimiter='\t', row_delimiter='\n'):
        with open(f'exports\\{file_name}.txt', 'w') as f:
            for point in self.sweep:
                for row in self.sweep[point]:
                    line = column_delimiter
                    for element in row:
                        line += f'{element:.4}{column_delimiter}'
                    line += row_delimiter
                    f.write(line)
                f.write(row_delimiter)

    def export_igor_text(self,
                         file_name,
                         column_delimiter='\t',
                         row_delimiter='\n'):
        with open(f'exports\\{file_name}.itx', 'w') as f:
            f.write(f'IGOR{row_delimiter}')
            f.write(f'WAVES/D/N=({len(self.sweep)}, 2) counts, time{row_delimiter}'
                    )  # FIXME: proper wave dimensions for arbitrary data
            f.write(f'BEGIN{row_delimiter}')
            for point in self.sweep:
                f.write(
                    f'{column_delimiter}{point}{column_delimiter}{sum(sum(self.sweep[point]))}{row_delimiter}'
                )
            f.write('END')

    def export_raw_igor_text(self,
                             file_name,
                             column_delimiter='\t',
                             row_delimiter='\n'):
        with open(f'exports\\{file_name}.itx', 'w') as f:
            f.write(f'IGOR{row_delimiter}')
            index = 0
            for point in self.sweep:
                index += 1
                shape = self.sweep[point].shape
                f.write(f'WAVES/D/N=({shape[0]}, {shape[1]}) delay_{index}{row_delimiter}'
                        )  # FIXME: proper wave dimensions for arbitrary data
                f.write(f'BEGIN{row_delimiter}')
                for row in self.sweep[point]:
                    line = column_delimiter
                    for element in row:
                        line += f'{element:.4}{column_delimiter}'
                    line += row_delimiter
                    f.write(line)
                f.write('END')
                f.write(row_delimiter)
            f.write(f'WAVES/D sweep_points{row_delimiter}')
            f.write(f'BEGIN{row_delimiter}')
            for point in self.sweep:
                f.write(f'{column_delimiter}{point}{row_delimiter}')
            f.write('END')
            f.write(row_delimiter)


class ExportWorker(QRunnable):

    def __init__(self, data, gui, is_export_raw):
        QRunnable.__init__(self)
        self.export_data: SweepData = data
        self.gui: DaqWindow = gui
        self.is_export_raw = is_export_raw

    @pyqtSlot()
    def run(self):
        try:
            if self.is_export_raw:
                self.gui.export_spectrum_indicator.set_ongoing()
                file_name = self.gui.export_spectrum_name_input.text(
                ) + f'_{self.gui.controls.current_sweep_value.text()}'
                if self.gui.export_spectrum_format.currentText() == 'txt':
                    self.export_data.export_raw(file_name)
                elif self.gui.export_spectrum_format.currentText() == 'itx':
                    self.export_data.export_raw_igor_text(file_name)
                self.gui.export_spectrum_indicator.set_blank()
            else:
                file_name = self.gui.export_sweep_name_input.text(
                ) + f'_{self.gui.controls.current_sweep_value.text()}'
                self.gui.export_sweep_indicator.set_ongoing()
                if self.gui.export_sweep_format.currentText() == 'txt':
                    self.export_data.export(file_name)
                elif self.gui.export_sweep_format.currentText() == 'itx':
                    self.export_data.export_igor_text(file_name)
                self.gui.export_sweep_indicator.set_blank()
        except Exception as e:
            if self.is_export_raw:
                self.gui.export_spectrum_indicator.set_fail()
            else:
                self.gui.export_sweep_indicator.set_fail()
            print(repr(e))


class Controls(QWidget):

    def __init__(self, spectrum, sweep_canvas, threadpool, gui):
        self.stage: StandaStage = None
        QWidget.__init__(self)
        self.setFixedSize(QSize(window_width // 3, window_height))
        self.spectrum = spectrum
        self.sweep_canvas = sweep_canvas
        self.threadpool = threadpool
        self.gui = gui
        self.controls_layout = QVBoxLayout()
        self.sweep_data: SweepData = None

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
        self.start_sweep = QVBoxLayout()
        self.start_sweep_button: QWidget = QPushButton("start sweep")
        self.start_sweep_button.clicked.connect(self.do_sweep)
        self.sweep_indicator = PointsSlider()
        self.sweep_point_indicator = QLabel()
        self.sweep_point_indicator.setFixedSize(QSize(30, 30))
        self.start_sweep.addWidget(self.start_sweep_button)
        self.start_sweep.addWidget(self.sweep_indicator)
        self.start_sweep.addWidget(self.sweep_point_indicator,
                                   alignment=Qt.AlignmentFlag.AlignHCenter)

        # stop sweep button
        self.stop_sweep = QPushButton('stop')
        self.stop_sweep.clicked.connect(self.do_stop_sweep)

        # get specturm button
        self.acquire = QPushButton("acquire")
        self.acquire.clicked.connect(self.scan_spectrum)

        # sweep configuration
        self.configuration = QVBoxLayout()

        # kinetic energy
        self.kinetic_energy = QHBoxLayout()
        self.KE_label = QLabel('kinetic energy (eV)')
        self.KE_input = QLineEdit('1.5')
        self.kinetic_energy.addWidget(self.KE_label)
        self.kinetic_energy.addWidget(self.KE_input)

        # pass energy
        self.pass_energy = QHBoxLayout()
        self.PE_label = QLabel('pass energy (a.u)')
        self.PE_input = QLineEdit('10')
        self.pass_energy.addWidget(self.PE_label)
        self.pass_energy.addWidget(self.PE_input)

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

        # save interval
        self.save_interval = QHBoxLayout()
        self.save_interval_label = QLabel('save every x sweeps')
        self.save_interval_input = QLineEdit('20')
        self.save_interval.addWidget(self.save_interval_label)
        self.save_interval.addWidget(self.save_interval_input)

        # current sweep
        self.current_sweep = QHBoxLayout()
        self.current_sweep_label = QLabel('current sweep')
        self.current_sweep_value = QLineEdit('0')
        self.current_sweep.addWidget(self.current_sweep_label)
        self.current_sweep.addWidget(self.current_sweep_value)

        # grouping configuration
        self.configuration.addLayout(self.kinetic_energy)
        self.configuration.addLayout(self.dwell_time)
        self.configuration.addLayout(self.pass_energy)
        self.configuration.addLayout(self.points)
        self.configuration.addLayout(self.save_interval)
        self.configuration.addLayout(self.current_sweep)

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
        self.set_new_t_0_position.clicked.connect(
            self.set_new_t_0_value_position)
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
        self.controls_layout.addWidget(self.acquire)
        self.controls_layout.addWidget(self.stop_sweep)
        self.controls_layout.addLayout(self.configuration)

        self.setLayout(self.controls_layout)

    def connect_to_analyser(self):
        worker = ConnectAnalyser(self)
        self.threadpool.start(worker)

    def connect_to_stage(self):
        worker = ConnectStage(self)
        self.threadpool.start(worker)

    def get_stage_position(self):
        self.stage_position_output.setText('{:10.4f}'.format(
            self.stage.get_pos_mm()))

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
        worker = AnalyserWorker(self, AnalyserMission.Sweep, self.gui)
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
        worker = AnalyserWorker(self, AnalyserMission.Aqcuire, self.gui)
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
        self.spectrum_layout = QVBoxLayout()
        self.spectrum = SpectrumCanvas()
        self.export_spectrum_controls = QHBoxLayout()
        self.export_spectrum_name_label = QLabel('file name')
        self.export_spectrum_name_input = QLineEdit('spectrum_data')
        self.export_spectrum_format = QComboBox()
        self.export_spectrum_format.addItems(['itx', 'txt'])
        self.export_spectrum_button = QPushButton('export spectrum data')
        self.export_spectrum_button.clicked.connect(self.do_export_spectrum)
        self.export_spectrum_indicator = Indicator()
        self.export_spectrum_controls.addWidget(
            self.export_spectrum_name_label)
        self.export_spectrum_controls.addWidget(
            self.export_spectrum_name_input)
        self.export_spectrum_controls.addWidget(self.export_spectrum_format)
        self.export_spectrum_controls.addWidget(self.export_spectrum_button)
        self.export_spectrum_controls.addWidget(self.export_spectrum_indicator)
        self.spectrum_layout.addWidget(self.spectrum)
        self.spectrum_layout.addLayout(self.export_spectrum_controls)

        # sweep
        self.sweep_layout = QVBoxLayout()
        self.sweep_canvas = SweepCanvas()
        self.export_sweep_controls = QHBoxLayout()
        self.export_sweep_name_label = QLabel('file name')
        self.export_sweep_name_input = QLineEdit('sweep_data')
        self.export_sweep_format = QComboBox()
        self.export_sweep_format.addItems(['itx', 'txt'])
        self.export_sweep_button = QPushButton('export sweep data')
        self.export_sweep_button.clicked.connect(self.do_export_sweep)
        self.export_sweep_indicator = Indicator()
        self.export_sweep_controls.addWidget(self.export_sweep_name_label)
        self.export_sweep_controls.addWidget(self.export_sweep_name_input)
        self.export_sweep_controls.addWidget(self.export_sweep_format)
        self.export_sweep_controls.addWidget(self.export_sweep_button)
        self.export_sweep_controls.addWidget(self.export_sweep_indicator)
        self.sweep_layout.addWidget(self.sweep_canvas)
        self.sweep_layout.addLayout(self.export_sweep_controls)

        self.results.addLayout(self.spectrum_layout)
        self.results.addLayout(self.sweep_layout)

        self.controls = Controls(self.spectrum, self.sweep_canvas,
                                 self.threadpool, self)

        self.layout.addWidget(self.controls)
        self.layout.addLayout(self.results)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)

    def do_export_sweep(self):
        worker = ExportWorker(self.controls.sweep_data,
                              self, is_export_raw=False)
        self.threadpool.start(worker)

    def do_export_spectrum(self):
        worker = ExportWorker(self.controls.sweep_data,
                              self, is_export_raw=True)
        self.threadpool.start(worker)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DaqWindow()
    window.show()
    app.exec()
