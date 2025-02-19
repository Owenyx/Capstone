from Controller import Controller
from time import sleep
controller = Controller()

connected = controller.find_and_connect()
if not connected:
    print('Failed to connect to sensor')
    exit()



print('Starting resist collection')
controller.start_resist_collection()
for i in range(5):
    sleep(1)
    print(f'Resist O1: {controller.deques["resist"]["O1"]["values"][-1]}')
    print(f'Resist O2: {controller.deques["resist"]["O2"]["values"][-1]}')
    print(f'Resist T3: {controller.deques["resist"]["T3"]["values"][-1]}')
    print(f'Resist T4: {controller.deques["resist"]["T4"]["values"][-1]}')
print('Stopping resist collection')
controller.stop_resist_collection()

battery_level = controller.battery_level
print(f'Battery level: {battery_level}')


print('Starting all data collection')
controller.start_all_data_collection()
while not controller.bipolar_is_calibrated or not controller.monopolar_is_calibrated:
    sleep(0.5)
    print(f'Bipolar calibration progress: {controller.bipolar_calibration_progress}')
    print(f'Monopolar calibration progress: {controller.monopolar_calibration_progress}')
sleep(10)
print('Stopping all data collection')
controller.stop_signal_collection()

print('Logging to file')
controller.log_deques_to_files()