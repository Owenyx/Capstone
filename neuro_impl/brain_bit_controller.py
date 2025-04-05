import contextlib
from threading import Thread

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from neurosdk.scanner import Scanner
from neurosdk.sensor import Sensor
from neurosdk.cmn_types import *


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, work):
        super().__init__()
        self.work = work

    def run(self):
        self.work()
        self.finished.emit()


class BrainBitController(QObject):
    sensorConnectionState = pyqtSignal(SensorState)

    def __init__(self):
        super().__init__()
        self.sensor = None
        self.scanner = Scanner([SensorFamily.LEBrainBit, SensorFamily.LECallibri])
        self.sensorsFounded = None
        self.sensorBattery = None
        self.resistReceived = None
        self.signalReceived = None
        self.thread = None
        self.worker = None

    def start_scan(self):
        if self.sensor is not None and self.sensor.state is SensorState.StateInRange:
            self.sensor.disconnect()
            del self.sensor
            self.sensor = None

        def sensors_founded(scanner, sensors):
            self.sensorsFounded(sensors)
        self.scanner.sensorsChanged = sensors_founded
        thread = Thread(target=self.scanner.start)
        thread.start()

    def stop_scan(self):
        self.scanner.stop()
        self.scanner.sensorsChanged = None

    def create_and_connect(self, sensor_info: SensorInfo):
        def device_connection():
            try:
                self.sensor = self.scanner.create_sensor(sensor_info)
            except Exception as err:
                print(err)
            if self.sensor is not None:
                self.sensor.sensorStateChanged = self.__connection_state_changed
                self.sensor.batteryChanged = self.__battery_changed
                if self.sensorConnectionState is not None:
                    self.sensorConnectionState.emit(SensorState.StateInRange)
            else:
                if self.sensorConnectionState is not None:
                    self.sensorConnectionState.emit(SensorState.StateOutOfRange)

        self.thread = QThread()
        self.worker = Worker(device_connection)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

    def disconnect_sensor(self):
        self.sensor.disconnect()

    def __connection_state_changed(self, sensor: Sensor, state: SensorState):
        if self.sensorConnectionState is not None:
            self.sensorConnectionState.emit(state)

    def __battery_changed(self, sensor: Sensor, battery: int):
        if self.sensorBattery is not None:
            self.sensorBattery(battery)

    def full_info(self):
        pass

    def start_resist(self):
        def resist_data_received(sensor, resist):
            self.resistReceived(resist)
        self.sensor.resistDataReceived = resist_data_received
        self.__execute_command(SensorCommand.StartResist)

    def stop_resist(self):
        self.__execute_command(SensorCommand.StopResist)
        self.sensor.resistDataReceived = None

    def start_signal(self):
        def signal_data_received(sensor, signal):
            self.signalReceived(signal)
        self.sensor.signalDataReceived = signal_data_received
        self.__execute_command(SensorCommand.StartSignal)

    def stop_signal(self):
        self.__execute_command(SensorCommand.StopSignal)
        self.sensor.signalDataReceived = None

    def __execute_command(self, command: SensorCommand):
        def execute_command():
            try:
                self.sensor.exec_command(command)
            except Exception as err:
                print(err)
        thread = Thread(target=execute_command)
        thread.start()

    def __del__(self):
        with contextlib.suppress(Exception):
            self.sensor.disconnect()
            del self.sensor


brain_bit_controller = BrainBitController()
