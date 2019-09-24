#!/usr/bin/env python3
from mixtape.players import AsyncPlayer as Player
import asyncio
import os
from dbus_next.service import ServiceInterface, method, dbus_property, signal, Variant
from dbus_next.aio import MessageBus
import logging 
import gi
import colorlog
import threading
gi.require_version("Gst", "1.0")
from gi.repository import Gst


LOG_LEVEL = os.environ.get("LOG_LEVEL", default="DEBUG")
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "(%(asctime)s) [%(log_color)s%(levelname)s] | %(name)s | %(message)s [%(threadName)-10s]"))

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)


Gst.init(None)

DBUS_NAME = "org.testcases.gst"
DBUS_PATH = "/org/testcases/gst"

# current workaround for display
O_H, O_W = 720, 1280
FACTOR = 1
W, H = 1920, 1080
W_SCREEN, H_SCREEN = int(W / FACTOR), int(H / FACTOR)
OFFSET_X, OFFSET_Y = 0, -100
X_OVERLAY = int((O_H-H_SCREEN)/2) + OFFSET_X
Y_OVERLAY = int((O_W-W_SCREEN)/2) + OFFSET_Y


GST_PIPE_TEST_OVERLAY = f"""videotestsrc ! 
    nvvidconv ! 
    video/x-raw(memory:NVMM), width=720, height=324, format=I420 ! 
    nvvidconv flip-method=0 ! 
    nvoverlaysink overlay-h={W_SCREEN} overlay-w={H_SCREEN} overlay-x={X_OVERLAY} overlay-y={Y_OVERLAY}
"""  

GST_PIPE_TEST_ENCODER = """videotestsrc ! 
    nvvidconv ! 
    video/x-raw(memory:NVMM), width=324, height=324, format=I420 ! 
    nvvidconv flip-method=1 ! queue ! omxvp8enc !  queue ! omxvp8dec ! nvvidconv ! 
    nvoverlaysink
"""  


class SimplePlayerInterface(ServiceInterface):
    
    NAME = "SimplePlayer"

    def __init__(self, base_path):
        interface_path = f"{base_path}.{self.NAME}"
        super().__init__(interface_path)
        self._player = None        
        self._state = None
        self._worker = None

    @method()
    def Echo(self, input: 's') -> 's':
        return input
    
    @method()
    def Init(self) -> 's':
        logger.debug("Init player")
        try:
            self._state = 0
            self._player, self._worker = self.setup_player()
        except Exception as e:
            logger.error(e)
            self._state = -1
            return 'Init NoOK'
        return 'Init OK'

    @method()
    def Play(self) -> 's':
        self._player.play()
        return 'Play OK'

    @method()
    def Pause(self) -> 's':
        self._player.play()
        return 'Play OK'

    @method()
    def Stop(self) -> 's':
        self._player.stop()
        return 'Stop OK'


    def setup_player(self, pipeline=None):
        if pipeline is None: 
            desc = GST_PIPE_TEST_OVERLAY 
        p = Player.from_description(desc)
        t = threading.Thread(target=lambda: p.run(autoplay=False))
        t.daemon = True
        t.start()
        return p, t
   

class GstDBusService:
    DBUS_NAME = "org.testcases.gst"
    DBUS_PATH = "/org/testcases/gst"
    INTERFACES = [SimplePlayerInterface]

    def __init__(self, bus_address):
        self.bus_address = bus_address

    async def run(self):
        self.bus = await MessageBus(bus_address=self.bus_address).connect()
        self.request = await self.bus.request_name(DBUS_NAME)
        for interface in self.INTERFACES:
            self.bus.export(DBUS_PATH, interface(DBUS_NAME))
        await asyncio.get_event_loop().create_future()

if __name__ == "__main__":
    with open(os.path.join('/tmp/dbus/cookie')) as f:
        address = f.readline().strip('\n')
    s = GstDBusService(address)
    logger.info("Starting service") 
    asyncio.get_event_loop().run_until_complete(s.run())