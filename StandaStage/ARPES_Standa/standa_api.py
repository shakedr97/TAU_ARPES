from ctypes import *
import os
import sys
try:
    from ARPES_Standa.ximc.pyximc import get_position_t
    from ARPES_Standa.ximc.pyximc import MicrostepMode
except Exception as e:
    print(e)

c = 299.792458 # mm / ns

cur_dir = os.path.abspath(os.path.dirname(__file__))
dll_path = os.path.join(cur_dir, 'ximc', 'dlls')
sys.path.append(os.path.join(cur_dir, 'ximc'))
os.add_dll_directory(dll_path)

from pyximc import *

class Standa:
    _lib = lib    

    def __init__(self):
        self.lib = lib

    def find_device() -> bytearray:
        # Set bindy (network) keyfile. Must be called before any call to "enumerate_devices" or "open_device" if you
        # wish to use network-attached controllers. Accepts both absolute and relative paths, relative paths are resolved
        # relative to the process working directory. If you do not need network devices then "set_bindy_key" is optional.
        # In Python make sure to pass byte-array object to this function (b"string literal").
        result = lib.set_bindy_key(os.path.join(cur_dir, "keyfile.sqlite").encode("utf-8"))
        if result != Result.Ok:
            lib.set_bindy_key("keyfile.sqlite".encode("utf-8")) # Search for the key file in the current directory.

        probe_flags = EnumerateFlags.ENUMERATE_PROBE + EnumerateFlags.ENUMERATE_NETWORK
        enum_hints = b"addr="
        devenum = Standa._lib.enumerate_devices(probe_flags, enum_hints)
        dev_count = Standa._lib.get_device_count(devenum)
        if dev_count > 1:
            raise Exception(f'found more than one device: {dev_count}')
        dev_name = Standa._lib.get_device_name(devenum, 0) # FIXME: handle more than one device
        if type(dev_name) is str:
            dev_name = dev_name.encode()
        if dev_name is None:
            raise Exception('no device found')
        print(f'\tOpening device {repr(dev_name)}')
        return Standa._lib.open_device(dev_name)

class EngineStep:
    def __init__(self, step: int, microstep: int):
        self.step = step
        self.microstep = microstep

class StandaStage(Standa):
    # TODO: what to do with results -1? most likely better not to ignore it
    # TODO: init location? restart?
    # 157.3667 mm -> 6280258
    # smaller number - longer optical path
    # 150.0000 mm -> 6000000
    stage_pos_in_mm = 38044
    stage_pos_in_fs = - 2 * c * stage_pos_in_mm / 1e6
    step_size = 1 # convert distance to time
    microstep_size = 1
    refresh_interval_ms = 100 # TODO: is it ok?

    def __init__(self, device_id: bytes):
        Standa.__init__(self)
        self._device_id = device_id
        self.microstep_settings = MicrostepMode.MICROSTEP_MODE_FULL
        self.zero_pos : int = 1500000
        # TODO: maybe set speed?
    
    def set_microstep(self, setting):
        eng = engine_settings_t()
        self.lib.get_engine_settings(self._device_id, byref(eng))
        eng.MicrostepMode = setting
        res = self.lib.set_engine_settings(self._device_id, byref(eng))
        self.microstep_settings = setting
        print(f'\tset engine settings {repr(setting)} result: {repr(res)}') # TODO: pretty display for engine settings
    
    def set_zero_pos(self, pos : int):
        self.zero_pos = pos
    
    def set_current_pos_zero_pos(self):
        self.zero_pos = self.get_pos()
    
    def go_to_time_fs(self, time_fs: int):
        new_pos = self.zero_pos + self.stage_pos_in_fs * time_fs
        self.move_to(round(new_pos))
    
    def move_time_step(self, step_fs: int):
        new_pos = self.get_pos() + self.stage_pos_in_fs * step_fs
        self.move_to(round(new_pos))
    
    def get_status(self):
        status = status_t()
        result = self.lib.get_status(device_id, byref(status))
        print("\tstatus result: " + repr(result))
        if result == Result.Ok:
            print("\tStatus.Ipwr: " + repr(status.Ipwr))
            print("\tStatus.Upwr: " + repr(status.Upwr))
            print("\tStatus.Iusb: " + repr(status.Iusb))
            print("\tStatus.Flags: " + repr(hex(status.Flags)))
    
    def go_left(self):
        res = self.lib.command_left(self._device_id)
        print(f'\tgo_left result: {repr(res)}')
    
    def go_right(self):
        res = self.lib.command_right(self._device_id)
        print(f'\tgo_right success {repr(res)}')
    
    def stop(self):
        res = self.lib.command_stop(self._device_id)
        print(f'\tstop result: {repr(res)}')
    
    def wait_to_stop(self):
        self.lib.command_wait_for_stop(self._device_id, StandaStage.refresh_interval_ms)
    
    def move(self, dt: int):
        # TODO: micropos is irrelevant, only pos
        # left - makes optic path longer, right - makes path shorter
        if dt < 0: # TODO: is right or left associated with a positive time difference
            self.go_left()
        if dt > 0:
            self.go_right()
        steps = self.dt_to_steps(dt)
        self.lib.command_move(self._device_id, steps.step, steps.microstep)
        print('\tmoving')
        self.wait_to_stop()
        print('\tdone moving')
        # TODO: print new position, and time
        
    def dt_to_steps(self, dt: int) -> EngineStep: # translate time difference to engine steps and microsteps
        microstep = StandaStage.microstep_size / (2 ** self.microstep_settings)
        steps = dt // self.step_size
        print(f'\tsteps: {steps}')
        microsteps = 0 # (dt % self.step_size) // microstep
        print(f'\tmicrosteps: {microsteps}')
        return EngineStep(steps, microsteps)
    
    def move_to(self, pos: int):
        self.lib.command_move(self._device_id, pos, 0)

    def dispose(self):
        self.lib.close_device(byref(cast(self._device_id, POINTER(c_int))))
        print("\tDone")
    
    def set_speed(self, speed):
        mvst = move_settings_t()
        result = self.lib.get_move_settings(device_id, byref(mvst))
        print(f'The speed was equal to {mvst.Speed}. We will change it to {speed}')
        mvst.Speed = speed
        result = self.lib.set_move_settings(device_id, byref(mvst))
        print(f'\tset_speed result: {rerpr(result)}')
    
    def get_pos(self) -> int:
        pos = get_position_t()
        res = self.lib.get_position(self._device_id, byref(pos))
        if res == Result.Ok:
            print(f'pos - {pos.Position} micropos - {pos.uPosition}')
        return pos.Position
    

    


# sanity
sbuf = create_string_buffer(64)
lib.ximc_version(sbuf)
print(f'stage libary version - {sbuf.raw.decode()}')
print('network controllers not setup here')

# device_id = 1
device_id = Standa.find_device()
device = StandaStage(device_id)
# stage.set_microstep(MicrostepMode.MICROSTEP_MODE_FRAC_256)
device.get_status()
# stage.dispose()
try:
    while sys.argv[1]:
        order = input('enter order: (find_device, get_status, set_microstep_{256, 128, 2}, set_{left, right}, move, set_speed, close_device, exit)\n')
        match order:
            case 'find_device':
                device_id = Standa.find_device()
                device = StandaStage(device_id)
            case 'get_status':
                device.get_status()
            case 'set_microtep_256':
                device.set_microstep(MicrostepMode.MICROSTEP_MODE_FRAC_256)
            case 'set_microstep_128':
                device.set_microstep(MicrostepMode.MICROSTEP_MODE_FRAC_128)
            case 'set_microstep_2':
                device.set_microstep(MicrostepMode.MICROSTEP_MODE_FRAC_2)
            case 'set_right':
                device.go_right()
            case 'set_left':
                device.go_left()
            case 'move':
                dt = float(input('enter time difference:\n'))
                device.move(dt)
            case 'set_speed':
                speed = float(input('enter speed:\n'))
                device.set_speed(speed)
            case 'close_device':
                device.dispose()
            case 'stop':
                device.stop()
            case 'move_to':
                pos = int(input('enter pos'))
                device.move_to(pos)
            case 'get_pos':
                device.get_pos()
            case 'exit':
                exit()
except Exception as e:
    print(e)
    print('done')





### Garbage dump