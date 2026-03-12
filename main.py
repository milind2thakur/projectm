"""Project M main entrypoint with a minimal command loop."""

from __future__ import annotations

import sys
from pathlib import Path

# Add local module folders with hyphenated names for direct imports.
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT / "ai-core"))
sys.path.append(str(PROJECT_ROOT / "tools"))
sys.path.append(str(PROJECT_ROOT / "security"))

from command_interpreter import CommandInterpreter
from security.sandbox_runner import SandboxRunner
from tool_router import ToolRouter


def main() -> None:
    interpreter = CommandInterpreter()
    router = ToolRouter()
    sandbox = SandboxRunner()

    print("Project M prototype started. Type 'exit' to quit.")

    while True:
        user_command = input("\nYou> ").strip()
        if user_command.lower() in {"exit", "quit"}:
            print("Project M shutting down.")
            break

        interpreted = interpreter.interpret(user_command)
        print(f"AI interpretation: {interpreted}")

        result = sandbox.execute(interpreted, lambda: router.route_and_execute(interpreted))
        print(f"System response: {result}")


if __name__ == "__main__":
    main()
