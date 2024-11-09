# build.py
import os
import subprocess
import sys
import venv
import platform

def check_python_version():
    if sys.version_info < (3, 12):
        print("Error: Python 3.12 or higher is required.")
        print(f"Current Python version is {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print("Please install Python 3.12 or higher and try again.")
        sys.exit(1)
    print(f"Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected. Proceeding with build.")

def create_virtual_environment():
    print("Creating virtual environment...")
    venv.create("venv", with_pip=True)

def activate_virtual_environment():
    if platform.system() == "Windows":
        activate_script = os.path.join("venv", "Scripts", "activate.bat")
    else:
        activate_script = os.path.join("venv", "bin", "activate")

    activate_command = f"call {activate_script}" if platform.system() == "Windows" else f"source {activate_script}"
    return activate_command

def install_requirements(python_executable):
    print("Installing required packages...")
    subprocess.check_call([python_executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([python_executable, "-m", "pip", "install", "PyQt5", "pyinstaller"])

def build_executable(python_executable, main_script="main.py", app_name=None):
    if app_name is None:
        app_name = os.path.splitext(main_script)[0]

    icon_path = "gear_icon.ico"
    if not os.path.exists(icon_path):
        print(f"Warning: Icon file '{icon_path}' not found!")
        return

    print(f"Building executable for {main_script}...")

    cmd = [
        python_executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
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
        exe_path = os.path.join('dist', app_name + ('.exe' if platform.system() == 'Windows' else ''))
        print(f"Executable path: {exe_path}")

        if os.path.exists(exe_path):
            print("Executable created successfully!")
        else:
            print("Executable creation may have failed!")

    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        sys.exit(1)

def main():
    check_python_version()
    create_virtual_environment()
    activate_cmd = activate_virtual_environment()

    if platform.system() == "Windows":
        python_executable = os.path.join("venv", "Scripts", "python.exe")
    else:
        python_executable = os.path.join("venv", "bin", "python")

    build_command = f"{activate_cmd} && {python_executable} -c \"import sys; from build import install_requirements, build_executable; install_requirements(sys.executable); build_executable(sys.executable)\""

    try:
        subprocess.check_call(build_command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
