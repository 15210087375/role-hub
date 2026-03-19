#!/usr/bin/env python3
import subprocess


TASK_DAILY = "BehaviorMemoryGitSyncDaily"
TASK_WEEKLY = "BehaviorMemoryGitSyncWeekly"
PY = r"C:\Users\hzhnz\AppData\Local\Python\pythoncore-3.14-64\python.exe"
SYNC = r"C:\Users\hzhnz\.behavior-memory\sync_memory.py"


def install_daily() -> None:
    cmd = (
        f'schtasks /Create /F /SC DAILY /ST 22:00 '
        f'/TN "{TASK_DAILY}" /TR "\"{PY}\" \"{SYNC}\" sync"'
    )
    subprocess.run(cmd, shell=True, check=True)
    print("installed daily sync task")


def install_weekly() -> None:
    cmd = (
        f'schtasks /Create /F /SC WEEKLY /D SUN /ST 22:10 '
        f'/TN "{TASK_WEEKLY}" /TR "\"{PY}\" \"{SYNC}\" sync"'
    )
    subprocess.run(cmd, shell=True, check=True)
    print("installed weekly sync task")


def uninstall() -> None:
    for name in [TASK_DAILY, TASK_WEEKLY]:
        subprocess.run(f'schtasks /Delete /F /TN "{name}"', shell=True, check=False)
    print("removed sync tasks")


if __name__ == "__main__":
    install_daily()
    install_weekly()
