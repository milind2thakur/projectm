# Project M

Project M is an experimental **AI-first operating system prototype** where a minimal assistant (orb interface) replaces a traditional desktop workflow.

## Vision

Users interact using natural language or voice commands such as:

- `open downloads`
- `find budget.xlsx`
- `show system info`

The AI layer interprets commands, routes them to safe tools, and returns results.

## Architecture

- `ai-core/`: command interpretation, prompt building, memory, and tool routing.
- `tools/`: safe wrappers for basic system actions.
- `voice/`: placeholders for speech-to-text and text-to-speech.
- `security/`: sandbox and permission-gating concepts.
- `ui/`: orb interface placeholder and desktop controller stub.
- `config/`: application settings.
- `scripts/`: helper scripts like model setup.
- `models/`: local model storage (excluded from git).

## Quick start

1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Place a GGUF model at `models/projectm.gguf`.
3. Run the prototype loop:
   ```bash
   python main.py
   ```

## Command flow

1. User enters a command.
2. `command_interpreter` generates a structured tool call JSON (e.g. `{"tool": "open_folder", "path": "~/Downloads"}`).
3. `tool_router` selects a tool.
4. `sandbox_runner` applies permission checks before execution.

Example:

`open downloads` → interpreted as `{"tool": "open_folder", "path": "~/Downloads"}` → routed to `tools/open_folder.py`.

## Current status

This is a starter architecture focused on modularity and safety concepts. Voice I/O and UI are placeholders for future expansion.
