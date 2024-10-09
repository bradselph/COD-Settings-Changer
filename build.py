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

    # Check if icon exists
    icon_path = "gear_icon.ico"
    if not os.path.exists(icon_path):
        print(f"Warning: Icon file '{icon_path}' not found!")
        return

    print(f"Building executable for {main_script}...")

    # Base command with icon
    cmd = [
        "pyinstaller",
        "--onefile",
        "--clean",
        "--name", app_name,
        "--noconsole",
        "--icon", icon_path,
        main_script,
        "--add-data", f"help_texts.py{os.pathsep}.",
        "--add-data", f"{icon_path}{os.pathsep}."
    ]

    try:
        subprocess.check_call(cmd)
        print("\nBuild complete! Your executable can be found in the 'dist' folder.")
        exe_path = os.path.join('dist', app_name + ('.exe' if sys.platform == 'win32' else ''))
        print(f"Executable path: {exe_path}")

        # Verify if the executable was created
        if os.path.exists(exe_path):
            print("✅ Executable created successfully!")
        else:
            print("❌ Executable creation may have failed!")

    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_requirements()

    main_script = sys.argv[1] if len(sys.argv) > 1 else "main.py"
    app_name = sys.argv[2] if len(sys.argv) > 2 else None

    build_executable(main_script, app_name)