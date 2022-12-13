import dearpygui.dearpygui as dpg

# def button_callback(sender, app_data, user_data):
#     print(f"sender is: {sender}")
#     print(f"app_data is: {app_data}")
#     print(f"user_data is: {dpg.get_value(slider_name)}")

# def print_value(sender, app_data, user_data):
#     print(f"sender is: {sender}")
#     print(f"app_data is: {app_data}")
#     print(f'user data is {user_data}')

# dpg.create_context()
# daq_name = 'TAU ARPES'
# slider_name = 'dwell_time'
# with dpg.window(label=daq_name, tag=daq_name):
#     dpg.add_text('hello')
#     dpg.add_button(label='single sweep', callback=button_callback, user_data='data')
#     dpg.add_input_text(label='kinetic energy', callback=print_value)
#     dpg.add_slider_float(tag=slider_name, label="dwell time", default_value=0.273, max_value=1, callback=print_value)

# dpg.create_viewport(title=daq_name, width=600, height=600)


# dpg.setup_dearpygui()
# dpg.show_viewport()
# dpg.set_primary_window(daq_name, True)
# dpg.start_dearpygui()
# dpg.destroy_context()

import pyqtgraph.examples

# pyqtgraph.examples.run()
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLineEdit, QLabel, QVBoxLayout, QMenu

import sys

class DaqWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TAU ARPES DAQ")
        self.setFixedSize(QSize(400, 300))
        self.button = QPushButton("start sweep")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.do_sweep)
        self.button.released.connect(self.doing_sweep)

        self.input = QLineEdit()
        self.label = QLabel()
        self.input.textChanged.connect(self.label.setText)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            # handle the left-button press in here
            self.label.setText("mousePressEvent LEFT")

        elif e.button() == Qt.MouseButton.MiddleButton:
            # handle the middle-button press in here.
            self.label.setText("mousePressEvent MIDDLE")

        elif e.button() == Qt.MouseButton.RightButton:
            # handle the right-button press in here.
            self.label.setText("mousePressEvent RIGHT")
    
    def contextMenuEvent(self, e):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))
        context.exec(e.globalPos())


    def do_sweep(self, checked):
        print(f"sweeping: {checked}")
    
    def doing_sweep(self):
        print(f"doing sweep: {self.button.isChecked()}")
        self.button.setText("sweeping")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DaqWindow()
    window.show()
    app.exec()