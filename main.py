import os
import sys
import io

# --- Environment Setup for Kivy and Logging Fixes ---
if sys.platform.startswith('win'):
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
if 'KIVY_WINDOW' not in os.environ:
    os.environ['KIVY_WINDOW'] = 'sdl2'

# --- Patch: Always ensure stdout/stderr are not None ---
if getattr(sys, 'frozen', False):  # Running as PyInstaller EXE
    if sys.stdout is None:
        sys.stdout = io.StringIO()
    if sys.stderr is None:
        sys.stderr = io.StringIO()

    # Patch Kivy logger to always write to file if no console
    import logging
    log_path = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), 'app.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.FileHandler(log_path, encoding='utf-8')]
    )
    # Patch kivy logger
    try:
        from kivy.logger import Logger
        from kivy.logger import LOG_LEVELS
        Logger.handlers = []  # Remove default handlers
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(LOG_LEVELS["info"])
        Logger.addHandler(file_handler)
        Logger.info("Logger patched for bundled Windows EXE.")
    except Exception as log_ex:
        print(f"Kivy logger patch failed: {log_ex}")

# --- Main Application Execution ---
try:
    from translator import TranslationApp

    if __name__ == '__main__':
        is_frozen = getattr(sys, 'frozen', False)
        print(f"Running application... (Frozen: {is_frozen})")
        print(f"Platform: {sys.platform}")
        if sys.platform.startswith('win'):
            print(f"KIVY_GL_BACKEND = {os.environ.get('KIVY_GL_BACKEND')}")
            print(f"KIVY_WINDOW = {os.environ.get('KIVY_WINDOW')}")
        TranslationApp().run()
except Exception as e:
    # If a crash occurs on startup, log it to a file for easier debugging.
    with open("error.log", "w", encoding="utf-8") as f:
        f.write("A critical error occurred during application startup:\n\n")
        f.write(str(e) + "\n\n")
        import traceback
        traceback.print_exc(file=f)
    # Also, print the error if a console is available.
    print(f"A critical error occurred. See error.log for details: {e}")
