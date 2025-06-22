import os
import sys
import io

# --- Environment Setup for Kivy ---

# 1. Set Kivy window and graphics backend to solve issues on some systems.
#    This must be done *before* any Kivy modules are imported.
if sys.platform.startswith('win'):
    # Use ANGLE for DirectX compatibility to avoid OpenGL errors in VMs
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

# 2. Set the window provider. 'sdl2' is standard and required by the backend.
if 'KIVY_WINDOW' not in os.environ:
    os.environ['KIVY_WINDOW'] = 'sdl2'

# 3. Redirect stdout and stderr for PyInstaller windowed apps on Windows.
#    This prevents the app from crashing if it tries to print to a non-existent console.
#    This is a common issue with apps built with --noconsole or --windowed.
if sys.platform.startswith('win') and getattr(sys, 'frozen', False):
    if sys.stdout is None:
        sys.stdout = io.StringIO()
    if sys.stderr is None:
        sys.stderr = io.StringIO()

# --- Main Application Execution ---

# Now that the environment is properly configured, we can safely import and run the app.
try:
    from translator import TranslationApp

    if __name__ == '__main__':
        # The 'frozen' attribute is set by PyInstaller when running as a bundled .exe
        is_frozen = getattr(sys, 'frozen', False)
        print(f"Running application... (Frozen: {is_frozen})")
        print(f"Platform: {sys.platform}")

        if sys.platform.startswith('win'):
            print(f"KIVY_GL_BACKEND = {os.environ.get('KIVY_GL_BACKEND')}")
            print(f"KIVY_WINDOW = {os.environ.get('KIVY_WINDOW')}")

        TranslationApp().run()

except Exception as e:
    # If a crash occurs on startup, log it to a file for easier debugging.
    # This is especially useful for tracking down issues in the bundled .exe.
    with open("error.log", "w", encoding="utf-8") as f:
        f.write("A critical error occurred during application startup:\n\n")
        f.write(str(e) + "\n\n")
        import traceback
        traceback.print_exc(file=f)

    # Also, print the error if a console is available.
    print(f"A critical error occurred. See error.log for details: {e}") 