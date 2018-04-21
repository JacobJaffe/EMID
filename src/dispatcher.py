from pythonosc import udp_client, osc_message_builder
from events import Event

class Dispatcher:
    def __init__(self, port, address='127.0.0.1'):
        self.PORT = port
        self.address = address
        self.client = udp_client.SimpleUDPClient(address, port)

    def send(self, event : Event):
        ''' Sends OSC message according to definition of event.
            Note that event.as_osc_message() returns
             2 arguments: address, and message. '''
        self.client.send_message(*event.as_osc_message())
