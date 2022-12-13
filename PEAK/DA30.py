import peak

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
        # spectrum.show(data_type=peak.PeakSpectrumType.Count)
        data = spectrum.count_data
        time_data = spectrum.time_data
        print(data.shape)