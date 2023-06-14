"""The main file that executes"""

from threading import Thread

from .interface import display
from .registry import setup
from .server import listen

setup()

Thread(target=listen, daemon=True).start()

display()
