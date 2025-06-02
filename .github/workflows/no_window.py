import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
os.environ['KIVY_NO_ARGS'] = '1'
from translator import TranslationApp
if __name__ == '__main__':
    TranslationApp().run()
