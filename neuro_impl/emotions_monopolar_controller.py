from em_st_artifacts.emotional_math import EmotionalMath
from em_st_artifacts.utils.lib_settings import MathLibSetting, ArtifactDetectSetting, ShortArtifactDetectSetting, \
    MentalAndSpectralSetting
from em_st_artifacts.utils.support_classes import RawChannelsArray

from neuro_impl.utils import BB_channels


class EmotionMonopolar:
    def __init__(self):
        mls = MathLibSetting(sampling_rate=250,
                             process_win_freq=25,
                             fft_window=500,
                             n_first_sec_skipped=4,
                             bipolar_mode=False,
                             squared_spectrum=True,
                             channels_number=1,
                             channel_for_analysis=0)
        ads = ArtifactDetectSetting(hanning_win_spectrum=True)
        sads = ShortArtifactDetectSetting()
        mss = MentalAndSpectralSetting(n_sec_for_averaging=4)
        calibration_length = 6
        nwins_skip_after_artifact = 5

        self.__maths = {BB_channels[i]: EmotionalMath(mls, ads, sads, mss) for i in range(4)}
        for i in range(4):
            self.__maths[BB_channels[i]].set_calibration_length(calibration_length)
            self.__maths[BB_channels[i]].set_mental_estimation_mode(False)
            self.__maths[BB_channels[i]].set_skip_wins_after_artifact(nwins_skip_after_artifact)
            self.__maths[BB_channels[i]].set_zero_spect_waves(True, 0, 1, 1, 1, 0)
            self.__maths[BB_channels[i]].set_spect_normalization_by_bands_width(True)

        self.__is_calibrated = {'O1': False, 'O2': False, 'T3': False, 'T4': False}
        self.isArtifactedSequenceCallback = None
        self.isBothSidesArtifactedCallback = None
        self.progressCalibrationCallback = None
        self.lastSpectralDataCallback = None
        self.rawSpectralDataCallback = None
        self.lastMindDataCallback = None

    def start_calibration(self):
        for i in range(4):
            self.__maths[BB_channels[i]].start_calibration()

    def process_data(self, brain_bit_data: []):
        o1Values = []
        o2Values = []
        t3Values = []
        t4Values = []
        for i in range(len(brain_bit_data)):
            o1Values.append(RawChannelsArray([brain_bit_data[i].O1]))
            o2Values.append(RawChannelsArray([brain_bit_data[i].O2]))
            t3Values.append(RawChannelsArray([brain_bit_data[i].T3]))
            t4Values.append(RawChannelsArray([brain_bit_data[i].T4]))
        try:
            self.__maths['O1'].push_data_arr(o1Values)
            self.__maths['O2'].push_data_arr(o2Values)
            self.__maths['T3'].push_data_arr(t3Values)
            self.__maths['T4'].push_data_arr(t4Values)
            for i in range(4):
                self.__maths[BB_channels[i]].process_data_arr()
        except Exception as err:
            print(err)
        self.__resolve_artifacted()

        self.__process_calibration()

        self.__resolve_spectral_data()
        self.__resolve_raw_spectral_data()
        self.__resolve_mind_data()

    def __resolve_artifacted(self):
        for i in range(4):
            # sequence artifacts
            is_artifacted_sequence = self.__maths[BB_channels[i]].is_artifacted_sequence()
            self.isArtifactedSequenceCallback(is_artifacted_sequence, BB_channels[i])

            # both sides artifacts
            is_both_side_artifacted = self.__maths[BB_channels[i]].is_both_sides_artifacted()
            self.isBothSidesArtifactedCallback(is_both_side_artifacted, BB_channels[i])

    def __process_calibration(self):
        for i in range(4):
            if self.__is_calibrated[BB_channels[i]]:
                continue
            self.__is_calibrated[BB_channels[i]] = self.__maths[BB_channels[i]].calibration_finished()
            if not self.__is_calibrated[BB_channels[i]]:
                progress = self.__maths[BB_channels[i]].get_calibration_percents()
                self.progressCalibrationCallback(progress, BB_channels[i])

    def __resolve_spectral_data(self):
        for i in range(4):
            if not self.__is_calibrated[BB_channels[i]]:
                continue
            spectral_values = self.__maths[BB_channels[i]].read_spectral_data_percents_arr()
            if len(spectral_values) > 0:
                spectral_val = spectral_values[-1]
                self.lastSpectralDataCallback(spectral_val, BB_channels[i])

    def __resolve_raw_spectral_data(self):
        for i in range(4):
            if not self.__is_calibrated[BB_channels[i]]:
                continue
            raw_spectral_values = self.__maths[BB_channels[i]].read_raw_spectral_vals()
            self.rawSpectralDataCallback(raw_spectral_values, BB_channels[i])

    def __resolve_mind_data(self):
        for i in range(4):
            if not self.__is_calibrated[BB_channels[i]]:
                continue
            mental_values = self.__maths[BB_channels[i]].read_mental_data_arr()
            if len(mental_values) > 0:
                self.lastMindDataCallback(mental_values[-1], BB_channels[i])
