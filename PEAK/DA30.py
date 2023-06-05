import peak


class DA30:

    LENS_MODE = 'DA30L_01'

    def __init__(self):
        self.peak = peak.PeakClient()
        self.peak.connect()

        self.analyser = self.peak.get_acquire_spectrum_client()
        self.analyser.connect() # TODO: context management
        self._is_measuring = False

    def do_measurement(self, kinetic_energy: float = 1.75, dwell_time: float = 1.0, pass_energy: float = 10) -> peak.PeakSpectrum:
        self.start_measurement(kinetic_energy, dwell_time, pass_energy)
        spectrum = self.take_measurement()
        self.stop_measurement()
        return spectrum

    def setup_measurement(self, kinetic_energy: float, dwell_time: float, pass_energy:float):
        self.analyser.set_pass_energy(pass_energy=pass_energy)
        self.analyser.set_lens_mode(DA30.LENS_MODE)
        self.analyser.set_acquisition_mode(peak.PeakAcquisitionMode.IMAGE)
        self.analyser.set_dwell_time(dwell_time=dwell_time)
        self.analyser.set_store_spectrum(False)
        self.analyser.set_store_acquisition_data(False)
        self.analyser.set_x_axis_mode(peak.PeakAxisMode.FIXED)
        self.analyser.set_x_axis_center(kinetic_energy)

    def start_measurement(self, kinetic_energy=1.75, dwell_time=1.0, pass_energy=10):
        self._is_measuring = True
        self.analyser.setup_spectrum()
        self.setup_measurement(kinetic_energy, dwell_time, pass_energy)
        self.analyser.set_user_data({'Test': 1}) # what does this mean?

    def take_measurement(self):
        self.analyser.clear_spectrum()
        self.analyser.acquire_spectrum()
        spectrum = self.analyser.get_spectrum()
        return spectrum

    def stop_measurement(self):
        try:
            self.analyser.finish_spectrum()
            self.analyser.finish_measurement()
        except Exception as e:
            print(e)
