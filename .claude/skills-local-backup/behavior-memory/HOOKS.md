# Auto Memory Hooks

This system now supports a session lifecycle hook model.

## 1) Session Start (load memory context)

```bash
python ~/.behavior-memory/auto_runtime.py --session-start "new chat"
```

This writes `~/.behavior-memory/.runtime/current_session.json` with:
- active preferences
- active constraints
- recent behavior/cognition patterns
- screenshot path and environment hints

It also writes `~/.behavior-memory/.runtime/active_prompt.txt`.
Use this file as a lightweight system/context prepend for new chats.

## 2) Session End (write memory layers)

Prepare a messages file:

```json
[
  {"role":"user","content":"..."},
  {"role":"assistant","content":"..."}
]
```

Then run:

```bash
python ~/.behavior-memory/auto_runtime.py --session-end --messages-file ./messages.json
```

This updates:
- `Memory/L0_状态层/*.json`
- `Memory/L1_情境层.yaml`
- `Memory/L2_行为层.yaml`
- `Memory/L3_认知层.yaml`

It also removes:
- `~/.behavior-memory/.runtime/current_session.json`
- `~/.behavior-memory/.runtime/active_prompt.txt`

## 3) Manage by skill command

```bash
python ~/.claude/skills/behavior-memory/persona_memory.py 状态
python ~/.claude/skills/behavior-memory/persona_memory.py 配置 获取 路径配置.screenshot_path
python ~/.claude/skills/behavior-memory/persona_memory.py 构建上下文
```

## 4) Fully automatic mode (installed)

`opencode.cmd` is wrapped to run hooks automatically:

- before opencode starts: `opencode_bridge.py pre`
- after opencode exits: `opencode_bridge.py post`

So you do not need to remember manual start/end commands.

Wrapper files:
- active wrapper: `D:\devTools\env\npm-global\opencode.cmd`
- backup original: `D:\devTools\env\npm-global\opencode.real.cmd`
- bridge script: `~/.behavior-memory/opencode_bridge.py`

To uninstall wrapper, run `install_opencode_wrapper.py` and call `uninstall()`.
