# build.py
import os
import subprocess
import sys

def install_requirements():
    try:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    except subprocess.CalledProcessError as e:
        print(f"Error installing PyInstaller: {e}")
        sys.exit(1)

def build_executable(main_script="main.py", app_name=None):
    if app_name is None:
        app_name = os.path.splitext(main_script)[0]

    print(f"Building executable for {main_script}...")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--clean",
        "--name", app_name,
        "--noconsole",
        main_script,
        "--add-data", "help_texts.py;."
    ]

    if os.path.exists("gear-icon.ico"):
        cmd.extend(["--icon", "gear-icon.ico"])

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        sys.exit(1)

    print(f"\nBuild complete! Your executable can be found in the 'dist' folder.")
    print(f"Executable path: {os.path.join('dist', app_name + ('.exe' if sys.platform == 'win32' else ''))}")

if __name__ == "__main__":
    install_requirements()

    main_script = sys.argv[1] if len(sys.argv) > 1 else "main.py"
    app_name = sys.argv[2] if len(sys.argv) > 2 else None

    build_executable(main_script, app_name)
