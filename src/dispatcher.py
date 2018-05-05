from pythonosc import udp_client, osc_message_builder, osc_bundle_builder
from events import Event

class Dispatcher:
    def __init__(self, port, address='127.0.0.1'):
        self.PORT = port
        self.address = address
        self.client = udp_client.SimpleUDPClient(address, port)

    def send(self, event : Event):
        ''' Sends OSC message according to definition of event.
            Note that event.as_osc_message() returns
             2 arguments: address, and message.
        '''
        address, message = event.as_osc_message()
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        msg = osc_message_builder.OscMessageBuilder(address=address)
        types = ['i']*2 + ['f']*4
        for item, type in zip(message, types):
            if item is None:
                item = 0
            if type == 'i':
                item = int(item)
            elif type == 'f':
                item = float(item)
            msg.add_arg(item, type)
        bundle.add_content(msg.build())
        bundle = bundle.build()
        self.client.send(bundle)
        # self.client.send_message(address, message)
