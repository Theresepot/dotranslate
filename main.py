import os
import sys

# Set Kivy environment variables for Windows compatibility
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_WINDOW'] = 'sdl2'

# Ensure sys.stdout and sys.stderr are not None (important for --windowed PyInstaller)
class DummyStream:
    def write(self, *args, **kwargs):
        pass
    def flush(self):
        pass

if sys.stdout is None:
    sys.stdout = DummyStream()
if sys.stderr is None:
    sys.stderr = DummyStream()

# Optionally, redirect to a log file instead:
# sys.stdout = open('dotranslate.log', 'a')
# sys.stderr = sys.stdout

# Now import and run the app
from translator import TranslationApp

if __name__ == '__main__':
    TranslationApp().run() 