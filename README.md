# Project M

Project M is an experimental **AI-first desktop shell prototype for Linux**. This version provides a minimal desktop window with a glowing orb that routes natural-language commands to safe local tools.

## Concept

Users issue natural-language commands (text or voice). Project M interprets intent, routes to safe tool wrappers, executes actions, and reports structured outcomes in the orb status area.

## Architecture

`User text/voice -> command interpreter -> tool router/workflows -> safe tool execution -> memory + telemetry -> UI result + next suggestions`

## Current Features

- Tkinter desktop orb window (`500x500`) with dark minimal design
- Orb states and colors:
  - idle (blue)
  - listening (purple)
  - thinking (orange)
  - executing (green)
- Command panel with text input + microphone trigger
- Rule-based command interpreter with optional `llama-cpp-python`
- Structured tool routing and responses
- Safe wrappers for app launch, folder open, file search, system usage, and install preview
- Permission gating (`read`, `write`, `admin`) and sandbox abstraction with exception-safe execution
- Confirmation queue for sensitive actions (`confirm` / `deny`)
- SQLite-backed command/result history (persistent memory)
- Terminal fallback mode when Tk/Tcl GUI is unavailable
- Real speech-to-text flow using `faster-whisper` + microphone capture (`sounddevice`)
- Optional text-to-speech responses via `pyttsx3`
- Push-to-talk hotkey support for voice capture
- Window control tools (`list`, `focus`, `minimize`, `close`)
- Workflow templates (`list workflows`, `run workflow <name>`)
- Adaptive planner (`plan goal`, `plan show`, `plan run`, `plan clear`)
- Telemetry JSONL event logging for demo traces
- Context-aware "next action" suggestions in terminal and GUI context panel
- Goal sessions (`goal <text>`, `goal status`, `goal clear`) with progress summaries
- Terminal meta commands: `help`, `history [n]`, `voice`, `ptt`, `resume`, `next`, and `goal`

## Folder Structure

- `ai_core/`: Interpreter, router, memory, prompt helper
- `tools/`: Safe action wrappers
- `security/`: Permission manager and sandbox abstraction
- `ui/`: Desktop orb window and related UI components
- `voice/`: STT/TTS modules
- `config/`: Settings file
- `scripts/`: Setup helpers
- `tests/`: Pytest coverage for parser/router/terminal/voice basics

## Configuration

`config/settings.yaml` supports:

- `mode`: `fallback` or model mode (`models/projectm.gguf`)
- `voice_enabled`: enable/disable voice capture + spoken responses
- `stt_model`: faster-whisper model size (`base` default)
- `voice_capture_seconds`: microphone capture duration per attempt
- `voice_capture_retries`: retry attempts when speech/noise fails
- `voice_push_to_talk_key`: keyboard key used to trigger push-to-talk
- `default_search_root`: root path for file search
- `allowed_apps`: app allowlist for `open <app>`
- `confirmation_enabled`: enable/disable confirmation queue
- `confirmation_required_tools`: tools that require confirmation
- `memory_db_path`: SQLite path for persistent memory entries
- `telemetry_enabled`: enable/disable telemetry events
- `telemetry_log_path`: JSONL output path for telemetry logs

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Voice capture dependencies (`numpy`, `sounddevice`) are included in `requirements.txt`.  
On Linux, make sure audio stack/device access is available for microphone capture.

## Run

```bash
python main.py
```

This launches the Project M orb desktop window.

If GUI startup fails (for example, missing Tk/Tcl), Project M automatically switches to terminal mode.

## Example Commands

- `open downloads`
- `open firefox`
- `show cpu usage`
- `show memory usage`
- `show storage usage`
- `install numpy`
- `find invoice`
- `voice` (terminal mode)
- `next` (show AI-suggested next actions)
- `resume` (re-run last task)
- `goal finish desktop demo` (set active goal)
- `goal status` (goal progress summary)
- `goal clear` (clear active goal)
- `plan goal` (generate plan from active goal)
- `plan show` (show plan progress and next steps)
- `plan run` (execute remaining plan steps)
- `plan clear` (clear active plan)
- `help`
- `history 10`

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

### V4
- Context-aware next-action guidance
- Workflow-first user journeys
- Demo telemetry and observability
- Goal-driven task sessions
- Adaptive goal-to-plan execution

## Safety Note

Project M V1 does **not** run dangerous commands automatically. Package installation is preview-only and returns a command requiring explicit confirmation in future versions.
