import peak

class DA30:

    def __init__(self):
        self.manager = peak.ManagerClient(f'http://localhost:8080/api')
        self.manager.connect()
        self.manager_status = self.manager.get_state()
        
        analyser = peak.WebsocketPeakClient(self.manager.server_address('Analyser'))
        analyser.connect()
        self.analyser = peak.AnalyserMeasurementController(analyser)
        self._is_measuring = False
    
    def do_measurement(self, kinetic_energy=1.75, dwell_time=1.0):
        seq_loq_id = 'test'
        acq_log_id = 'test'
        self.analyser.start_measurement(seq_loq_id, acq_log_id)

        configuration_name = self.analyser.configuration_name
        spectrum_definition = {
                        'ElementSetName': configuration_name,
                        'Name': 'DA30_Test',
                        'LensModeName': 'DA30L_01',
                        'PassEnergy': 10,
                        'FixedAxes': {'X': {'Center': kinetic_energy}},
                        'AcquisitionMode' : 'Image', 
                        'DwellTime' : dwell_time,
                        'StoreSpectrum': False,
                        'StoreAcquisitionData': False,
                        }    

        self.spectrum_id = self.analyser.define_spectrum(spectrum_definition)
        self.analyser.setup_spectrum(self.spectrum_id)
        self.analyser.acquire(self.spectrum_id)
        spectrum = self.analyser.get_measured_spectrum(self.spectrum_id)
        self.analyser.finish_spectrum(self.spectrum_id)
        self.analyser.finish_measurement()
        return spectrum
    
    def start_measurement(self, kinetic_energy=1.75, dwell_time=1.0):
        seq_loq_id = 'test'
        acq_log_id = 'test'
        self.analyser.start_measurement(seq_loq_id, acq_log_id)

        configuration_name = self.analyser.configuration_name
        spectrum_definition = {
                        'ElementSetName': configuration_name,
                        'Name': 'DA30_Test',
                        'LensModeName': 'DA30L_01',
                        'PassEnergy': 10,
                        'FixedAxes': {'X': {'Center': kinetic_energy}},
                        'AcquisitionMode' : 'Image', 
                        'DwellTime' : dwell_time,
                        'StoreSpectrum': False,
                        'StoreAcquisitionData': False,
                        }    

        self.spectrum_id = self.analyser.define_spectrum(spectrum_definition)
        self.analyser.setup_spectrum(self.spectrum_id)
        self._is_measuring = True
    
    def take_measurement(self):
        self.analyser.acquire(self.spectrum_id)
        spectrum = self.analyser.get_measured_spectrum(self.spectrum_id)
        self.analyser.clear_spectrum(self.spectrum_id)
        return spectrum

    def stop_measurement(self):
        try:
            self.analyser.finish_spectrum(self.spectrum_id)
            self.analyser.finish_measurement()
        except Exception as e:
            print(e)

test = 'data'

if __name__ == '__main__':
    if test == 'analyser':
        host = peak.host_address()
        print (host)
        manager = peak.ManagerClient(f'http://{host}:8080/api')
        manager.connect()
        state = manager.get_state()
        print(state)

        analyser_addr = manager.server_address('Analyser')
        manager.close()

        analyser_ws = peak.WebsocketPeakClient(analyser_addr)
        analyser_ws.connect()

        analyser = peak.AnalyserMeasurementController(analyser_ws)

        seq_loq_id = 'test'
        acq_log_id = 'test'
        analyser.start_measurement(seq_loq_id, acq_log_id)

        configuration_name = analyser.configuration_name
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

        spectrum_id = analyser.define_spectrum(spectrum_definition)
        analyser.setup_spectrum(spectrum_id)
        analyser.acquire(spectrum_id)

        spectrum = analyser.get_measured_spectrum(spectrum_id)

        # shutting down
        analyser.finish_spectrum(spectrum_id)
        analyser.finish_measurement()
        analyser_ws.close()
    elif test == 'data':
        print('testing data')
        base_dir = 'D:\git\TAU_ARPES\Spectrum_1'
        spectrum_id = '38eb55cb-c861-45ae-8103-20531210ae95'
        spectrum = peak.PeakSpectrum()
        spectrum.create_from_file(base_dir=base_dir, spectrum_id=spectrum_id)
        spectrum.show(data_type=peak.PeakSpectrumType.Count)
        data = spectrum.count_data
        time_data = spectrum.time_data
        print(data.shape)
