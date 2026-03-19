#!/usr/bin/env python3
import subprocess


TASK_NAME = "BehaviorMemoryMonthlyReport"
PY = r"C:\Users\hzhnz\AppData\Local\Python\pythoncore-3.14-64\python.exe"
CORE = r"C:\Users\hzhnz\.behavior-memory\persona_core.py"


def install() -> None:
    cmd = (
        f'schtasks /Create /F /SC MONTHLY /D 1 /ST 21:15 '
        f'/TN "{TASK_NAME}" /TR "\"{PY}\" \"{CORE}\" --monthly-report --months 1"'
    )
    subprocess.run(cmd, shell=True, check=True)
    print("installed monthly task")


def uninstall() -> None:
    cmd = f'schtasks /Delete /F /TN "{TASK_NAME}"'
    subprocess.run(cmd, shell=True, check=False)
    print("removed monthly task")


if __name__ == "__main__":
    install()
