import os
import sys

# Set Kivy environment variables for cross-platform compatibility
os.environ['KIVY_WINDOW'] = 'sdl2'
if sys.platform.startswith('win'):
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
else:
    # On Linux, let Kivy auto-detect or use 'gl' (default)
    os.environ.pop('KIVY_GL_BACKEND', None)

# --- Universal tessdata auto-detection ---
def find_tessdata_dir():
    if sys.platform.startswith('win'):
        # Try common Windows install locations
        possible = [
            r'C:\Program Files\Tesseract-OCR\tessdata',
            r'C:\Program Files (x86)\Tesseract-OCR\tessdata',
        ]
        for p in possible:
            if os.path.isdir(p):
                return p
    else:
        # Linux
        for p in [
            '/usr/share/tesseract-ocr/5/tessdata',
            '/usr/share/tesseract-ocr/4.00/tessdata',
            '/usr/share/tesseract-ocr/tessdata',
        ]:
            if os.path.isdir(p):
                return p
    return None

TESSDATA_DIR = find_tessdata_dir()
if TESSDATA_DIR:
    os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR

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

# Now import and run the app
from translator import TranslationApp

if __name__ == '__main__':
    TranslationApp().run() 