#!/usr/bin/env python3
from mixtape.players import AsyncPlayer as Player

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

Gst.init(None)

GST_PIPE_DESC = """videotestsrc ! 
    nvvidconv ! 
    video/x-raw(memory:NVMM), width=324, height=324, format=I420 ! 
    nvvidconv flip-method=1 ! 
    nvoverlaysink
"""  


if __name__ == "__main__":
    p = Player.from_description(GST_PIPE_DESC)
    p.run()