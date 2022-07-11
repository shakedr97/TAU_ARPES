import dataclasses

from numpy import double

@dataclasses.dataclass
class DetectorRegion:
    first_x_channel: int = 0
    last_x_channel: int = 800
    first_y_channel: int = 0
    last_y_channel: int = 600

    n_slices: int = 1

    is_adc_mode: bool = False

    def from_c(self, p_struct):
        self.first_x_channel = p_struct.firstXChannel_
        self.first_y_channel = p_struct.firstYChannel_
        self.last_x_channel = p_struct.lastXChannel_
        self.last_y_channel = p_struct.lastYChannel_
        self.n_slices = p_struct.slices_
        self.is_adc_mode = bool(p_struct.adcMode_)
    
    def into_c(self, ffi):
        p_struct = ffi.new('struct DetectorRegion *')
        p_struct.firstXChannel_ = self.first_x_channel
        p_struct.lastXChannel_ = self.last_x_channel
        p_struct.firstYChannel_ = self.first_y_channel
        p_struct.lastYChannel_ = self.last_y_channel
        p_struct.slices_ = self.n_slices
        p_struct.adcMode_ = 1 if self.is_adc_mode else 0

        return p_struct

@dataclasses.dataclass
class DetectorInfo:
    is_timer_controlled: bool = False # TODO: proper default

    num_x_channels: int = 100 # TODO: proper default
    num_y_channels: int = 100 # TODO: proper default
    max_slices: int = 500 # TODO: proper default
    max_channels: int = 500 # TODO: proper default
    frame_rate: int = 100 # TODO: proper default, units in name

    is_adc_present: bool = False # TODO: proper default
    is_disc_present: bool = False # TODO: proper default

    def from_c(self, p_struct):
        self.is_timer_controlled = p_struct.timerControlled_
        self.num_x_channels = p_struct.xChannels_
        self.num_y_channels = p_struct.yChannels_
        self.max_slices = p_struct.maxSlices_
        self.max_channels = p_struct.maxChannels_
        self.frame_rate = p_struct.frameRate_
        self.is_adc_present = p_struct.adcPresent_
        self.is_disc_present = p_struct.discPresent_
    
    def into_c(self, ffi):
        p_struct = ffi.new('struct DetectorInfo *')
        p_struct.timerControlled_ = self.is_timer_controlled
        p_struct.xChannels_ = self.num_x_channels
        p_struct.yChannels_ = self.num_y_channels
        p_struct.maxSlices_ = self.max_slices
        p_struct.maxChannels_ = self.max_channels
        p_struct.frameRate_ = self.frame_rate
        p_struct.adcPresent_ = self.is_adc_present
        p_struct.discPresent_ = self.is_disc_present
    
@dataclasses.dataclass
class AnalyzerRegion:
    is_fixed: bool = False # TODO: proper default

    energy_upper_bound: double = 20 # TODO: proper default, units
    energy_lower_bound: double = 1 # TODO: proper default, units
    center_energy: double = 10 # TODO: proper default, units, is necessary?
    energy_step: double = 0.5 # TODO: proper default, units
    dwell_time: int = 0.5 # TODO: proper default, units

    def from_c(self, p_struct):
        self.is_fixed = p_struct.fixed_
        self.energy_upper_bound = p_struct.highEnergy_
        self.energy_lower_bound = p_struct.lowEnergy_
        self.center_energy = p_struct.centerEnergy_
        self.energy_step = p_struct.energyStep_
        self.dwell_time = p_struct.dwellTime_
    
    def into_c(self, ffi):
        p_struct = ffi.new('struct AnalyzerRegion *')
        p_struct.fixed_ = self.is_fixed
        p_struct.highEnergy_ = self.energy_upper_bound
        p_struct.lowEnergy_ = self.energy_lower_bound
        p_struct.centerEnergy_ = self.center_energy
        p_struct.energyStep_ = self.energy_step
        p_struct.dwellTime_ = self.dwell_time