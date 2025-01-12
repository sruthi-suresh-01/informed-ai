import os
import subprocess
import sys
from dataclasses import dataclass

from rich.console import Console

# Get the absolute path to pyproject.toml
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PYPROJECT_PATH = os.path.join(ROOT_DIR, "pyproject.toml")


@dataclass
class Check:
    name: str
    command: list[str]


def run_check(check: Check) -> tuple[bool, str]:
    try:
        subprocess.run(
            check.command, check=True, capture_output=True, text=True, cwd=ROOT_DIR
        )
        return True, ""
    except subprocess.CalledProcessError as e:
        return False, e.stdout + e.stderr


def main():
    console = Console()

    # Match the checks from Makefile's code-validate target
    checks = [
        Check("poetry lock file", ["poetry", "check", "--lock"]),
        Check("black", ["poetry", "run", "black", "--config", PYPROJECT_PATH, "."]),
        Check("pyright", ["poetry", "run", "pyright", "--project", PYPROJECT_PATH]),
        Check(
            "mypy",
            ["poetry", "run", "mypy", "--config-file", PYPROJECT_PATH, "informed"],
        ),
        Check(
            "deptry",
            [
                "poetry",
                "run",
                "deptry",
                ".",
                "--config",
                PYPROJECT_PATH,
                "--extend-exclude",
                ".*/node_modules/",
            ],
        ),
    ]

    failed = False

    for check in checks:
        with console.status(f"Running {check.name}..."):
            success, output = run_check(check)
            if success:
                console.print(f"[green]OK[/green] {check.name}")
            else:
                console.print(f"[red]FAIL[/red] {check.name}")
                console.print(output)
                failed = True

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
