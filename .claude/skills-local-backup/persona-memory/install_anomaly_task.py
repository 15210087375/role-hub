#!/usr/bin/env python3
import subprocess


TASK_NAME = "BehaviorMemoryDailyAnomalyReminder"
PY = r"C:\Users\hzhnz\AppData\Local\Python\pythoncore-3.14-64\python.exe"
CORE = r"C:\Users\hzhnz\.behavior-memory\persona_core.py"


def install() -> None:
    cmd = (
        f'schtasks /Create /F /SC DAILY /ST 21:30 '
        f'/TN "{TASK_NAME}" /TR "\"{PY}\" \"{CORE}\" --refresh-anomaly-reminder"'
    )
    subprocess.run(cmd, shell=True, check=True)
    print("installed daily anomaly reminder task")


def uninstall() -> None:
    cmd = f'schtasks /Delete /F /TN "{TASK_NAME}"'
    subprocess.run(cmd, shell=True, check=False)
    print("removed daily anomaly reminder task")


if __name__ == "__main__":
    install()
