from em_st_artifacts.emotional_math import EmotionalMath
from em_st_artifacts.utils.lib_settings import MathLibSetting, ArtifactDetectSetting, ShortArtifactDetectSetting, \
    MentalAndSpectralSetting
from em_st_artifacts.utils.support_classes import RawChannels


class EmotionBipolar:
    def __init__(self):
        mls = MathLibSetting(sampling_rate=250,
                             process_win_freq=25,
                             fft_window=500,
                             n_first_sec_skipped=4,
                             bipolar_mode=True,
                             squared_spectrum=True,
                             channels_number=1,
                             channel_for_analysis=0)
        ads = ArtifactDetectSetting(hanning_win_spectrum=True)
        sads = ShortArtifactDetectSetting()
        mss = MentalAndSpectralSetting(n_sec_for_averaging=4)
        calibration_length = 6
        nwins_skip_after_artifact = 5

        self.__math = EmotionalMath(mls, ads, sads, mss)
        self.__math.set_calibration_length(calibration_length)
        self.__math.set_mental_estimation_mode(False)
        self.__math.set_skip_wins_after_artifact(nwins_skip_after_artifact)
        self.__math.set_zero_spect_waves(True, 0, 1, 1, 1, 0)
        self.__math.set_spect_normalization_by_bands_width(True)

        self.__is_calibrated = False
        self.isArtifactedSequenceCallback = None
        self.isBothSidesArtifactedCallback = None
        self.progressCalibrationCallback = None
        self.lastSpectralDataCallback = None
        self.rawSpectralDataCallback = None
        self.lastMindDataCallback = None

    def start_calibration(self):
        self.__math.start_calibration()

    def process_data(self, brain_bit_data: []):
        bipolar_samples = []
        for sample in brain_bit_data:
            left_bipolar = sample.T3 - sample.O1
            right_bipolar = sample.T4 - sample.O2
            bipolar_samples.append(RawChannels(left_bipolar, right_bipolar))
        self.__math.push_data(bipolar_samples)
        self.__math.process_data_arr()

        self.__resolve_artifacted()

        if not self.__is_calibrated:
            self.__process_calibration()
        else:
            self.__resolve_spectral_data()
            self.__resolve_raw_spectral_data()
            self.__resolve_mind_data()

    def __resolve_artifacted(self):
        # sequence artifacts
        is_artifacted_sequence = self.__math.is_artifacted_sequence()
        self.isArtifactedSequenceCallback(is_artifacted_sequence)

        # both sides artifacts
        is_both_side_artifacted = self.__math.is_both_sides_artifacted()
        self.isBothSidesArtifactedCallback(is_both_side_artifacted)

    def __process_calibration(self):
        self.__is_calibrated = self.__math.calibration_finished()
        if not self.__is_calibrated:
            progress = self.__math.get_calibration_percents()
            self.progressCalibrationCallback(progress)

    def __resolve_spectral_data(self):
        spectral_values = self.__math.read_spectral_data_percents_arr()
        if len(spectral_values) > 0:
            spectral_val = spectral_values[-1]
            self.lastSpectralDataCallback(spectral_val)

    def __resolve_raw_spectral_data(self):
        raw_spectral_values = self.__math.read_raw_spectral_vals()
        self.rawSpectralDataCallback(raw_spectral_values)

    def __resolve_mind_data(self):
        mental_values = self.__math.read_mental_data_arr()
        if len(mental_values) > 0:
            self.lastMindDataCallback(mental_values[-1])
