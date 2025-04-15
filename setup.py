from cx_Freeze import Executable, setup

executables = [Executable("main.py")]

setup(
    name="hello",
    version="0.1",
    description="Sample cx_Freeze script",
    executables=executables,
)