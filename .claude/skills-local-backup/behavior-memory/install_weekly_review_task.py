#!/usr/bin/env python3
import subprocess


TASK_NAME = "BehaviorMemoryWeeklyReview"
PY = r"C:\Users\hzhnz\AppData\Local\Python\pythoncore-3.14-64\python.exe"
CORE = r"C:\Users\hzhnz\.behavior-memory\persona_core.py"


def install() -> None:
    cmd = (
        f'schtasks /Create /F /SC WEEKLY /D SUN /ST 21:00 '
        f'/TN "{TASK_NAME}" /TR "\"{PY}\" \"{CORE}\" --weekly-review --days 7"'
    )
    subprocess.run(cmd, shell=True, check=True)
    print("installed weekly task")


def uninstall() -> None:
    cmd = f'schtasks /Delete /F /TN "{TASK_NAME}"'
    subprocess.run(cmd, shell=True, check=False)
    print("removed weekly task")


if __name__ == "__main__":
    install()
