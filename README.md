# Project M

Project M is an experimental **AI-first desktop shell prototype for Linux**. This version provides a minimal desktop window with a glowing orb that routes natural-language commands to safe local tools.

## Concept

Users issue natural-language commands (text first, voice-ready later). Project M interprets intent, routes to safe tool wrappers, executes actions, and reports structured outcomes in the orb status area.

## Architecture

`User text/voice -> Agent Engine -> command interpreter -> task planner -> execution manager -> tool router -> safe tool execution -> UI result`

## Current Features (V1 Prototype)

- Tkinter desktop orb window (`500x500`) with dark minimal design
- Orb states and colors:
  - idle (blue)
  - listening (purple)
  - thinking (orange)
  - executing (green)
- Command panel with input + microphone placeholder button
- Rule-based command interpreter with optional `llama-cpp-python`
- Structured tool routing and responses
- Safe wrappers for app launch, folder open, file search, system usage, and install preview
- Permission gating (`read`, `write`, `admin`) and sandbox abstraction
- In-memory command/result history


## Agent Engine (New)

Project M now routes each command through an Agent Engine lifecycle:

`input -> interpret -> plan -> execute -> memory`

The `agent/` subsystem provides:

- `agent_engine.py`: orchestration controller
- `task_planner.py`: builds executable step plans (single-step in V1)
- `execution_manager.py`: runs steps sequentially with error handling
- `agent_state.py`: tracks `IDLE/LISTENING/THINKING/EXECUTING/ERROR`

## Folder Structure

- `agent/`: Agent orchestration, planning, execution, and state
- `ai_core/`: Interpreter, router, memory, prompt helper
- `tools/`: Safe action wrappers
- `security/`: Permission manager and sandbox abstraction
- `ui/`: Desktop orb window and related UI components
- `voice/`: STT/TTS placeholders
- `config/`: Settings file
- `scripts/`: Setup helpers
- `tests/`: Pytest coverage for parser/router basics

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

This launches the Project M orb desktop window when a display server is available. In headless environments, Project M automatically falls back to a CLI loop. In either mode, type `exit` or `quit` to close.

## Example Commands

- `open downloads`
- `open firefox`
- `show cpu usage`
- `show memory usage`
- `show storage usage`
- `install numpy`
- `find invoice`

## Roadmap

### V1
- Desktop orb window
- Stable fallback parser
- Safe local tools
- Basic permission model

### V2
- Real voice input/output wiring
- Global hotkey and summon behavior
- Confirmed admin action flow

### V3
- Deeper desktop/window control
- Model-assisted orchestration with memory context
- Plugin/tool ecosystem

## Safety Note

Project M V1 does **not** run dangerous commands automatically. Package installation is preview-only and returns a command requiring explicit confirmation in future versions.
