#!/usr/bin/env python3
from pathlib import Path


OPENCODE_CMD = Path(r"D:\devTools\env\npm-global\opencode.cmd")
BACKUP_CMD = Path(r"D:\devTools\env\npm-global\opencode.real.cmd")
OPENCODE_PS1 = Path(r"D:\devTools\env\npm-global\opencode.ps1")
BACKUP_PS1 = Path(r"D:\devTools\env\npm-global\opencode.real.ps1")


def main() -> None:
    restored = False
    if BACKUP_CMD.exists():
        OPENCODE_CMD.write_text(BACKUP_CMD.read_text(encoding="utf-8"), encoding="utf-8")
        restored = True
    if BACKUP_PS1.exists():
        OPENCODE_PS1.write_text(BACKUP_PS1.read_text(encoding="utf-8"), encoding="utf-8")
        restored = True

    if restored:
        print("wrapper removed, original opencode launcher restored")
    else:
        print("backup not found, nothing to restore")


if __name__ == "__main__":
    main()
