from py4j.java_gateway import JavaGateway, GatewayServer
from EEG_Controller import Controller as EEGController
from HEG_Controller import HEGController

gateway = JavaGateway()
controller = gateway.jvm.Controller()


class EEGGateway(EEGController):
    def __init__(self):
        super().__init__()  # Initialize the parent EEGController
        # Start the gateway server
        self.gateway = GatewayServer(self)
        self.gateway.start()
        print("Gateway Server Started")
    
    def cleanup(self):
        # Make sure to add cleanup method to stop the gateway
        self.gateway.shutdown()
        super().cleanup()  # Call parent's cleanup if it exists

if __name__ == "__main__":
    eeg = EEGGateway()
    # Keep the program running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        eeg.cleanup()
        
        

class HEGGateway(HEGController):
    pass
