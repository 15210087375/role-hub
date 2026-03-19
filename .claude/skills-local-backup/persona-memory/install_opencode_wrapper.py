#!/usr/bin/env python3
from pathlib import Path


OPENCODE_CMD = Path(r"D:\devTools\env\npm-global\opencode.cmd")
BACKUP_CMD = Path(r"D:\devTools\env\npm-global\opencode.real.cmd")
OPENCODE_PS1 = Path(r"D:\devTools\env\npm-global\opencode.ps1")
BACKUP_PS1 = Path(r"D:\devTools\env\npm-global\opencode.real.ps1")
LAUNCHER = Path.home() / ".behavior-memory" / "opencode_launcher.py"


WRAPPER = r"""@ECHO off
SETLOCAL

set "MEM_LAUNCHER={launcher}"

if exist "%MEM_LAUNCHER%" (
  python "%MEM_LAUNCHER%" %*
  exit /b %ERRORLEVEL%
)

call "{real}" %*
exit /b %ERRORLEVEL%
"""

WRAPPER_PS1 = r"""#!/usr/bin/env pwsh
$launcher = "{launcher}"
$real = "{real}"

if (Test-Path $launcher) {{
  & "python" $launcher @args
  exit $LASTEXITCODE
}}

& $real @args
exit $LASTEXITCODE
"""


def install() -> None:
    if not OPENCODE_CMD.exists():
        raise FileNotFoundError(f"opencode.cmd not found: {OPENCODE_CMD}")

    if not BACKUP_CMD.exists():
        BACKUP_CMD.write_text(OPENCODE_CMD.read_text(encoding="utf-8"), encoding="utf-8")

    content = WRAPPER.format(launcher=str(LAUNCHER), real=str(BACKUP_CMD))
    OPENCODE_CMD.write_text(content, encoding="utf-8")

    if OPENCODE_PS1.exists():
        if not BACKUP_PS1.exists():
            BACKUP_PS1.write_text(OPENCODE_PS1.read_text(encoding="utf-8"), encoding="utf-8")
        content_ps1 = WRAPPER_PS1.format(launcher=str(LAUNCHER), real=str(BACKUP_PS1))
        OPENCODE_PS1.write_text(content_ps1, encoding="utf-8")

    print("installed")


def uninstall() -> None:
    if BACKUP_CMD.exists():
        OPENCODE_CMD.write_text(BACKUP_CMD.read_text(encoding="utf-8"), encoding="utf-8")
    if BACKUP_PS1.exists():
        OPENCODE_PS1.write_text(BACKUP_PS1.read_text(encoding="utf-8"), encoding="utf-8")
    print("uninstalled")


if __name__ == "__main__":
    install()
