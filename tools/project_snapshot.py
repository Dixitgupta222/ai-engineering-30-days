
from pathlib import Path
import subprocess
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "project_snapshot.txt"

SKIP_DIRS = {
    ".git", ".venv", "venv", "__pycache__",
    "node_modules", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "htmlcov", "dist", "build"
}

SKIP_NAMES = {
    ".env", ".env.local", ".env.production",
    "secrets.json", "credentials.json"
}

ALLOWED_EXTENSIONS = {
    ".py", ".toml", ".ini", ".cfg", ".md", ".txt",
    ".sql", ".yml", ".yaml"
}


def run_git(*args):
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
    except subprocess.CalledProcessError as error:
        return error.output.strip()


def should_include(path):
    relative = path.relative_to(ROOT)

    if any(part in SKIP_DIRS for part in relative.parts):
        return False

    if path.name in SKIP_NAMES:
        return False

    if path.suffix not in ALLOWED_EXTENSIONS:
        return False

    # Avoid including the generated report itself.
    if path == OUTPUT:
        return False

    return True


def main():
    sections = [
        "AI LEAD ANALYZER — PROJECT SNAPSHOT",
        f"Generated: {datetime.now().astimezone().isoformat()}",
        f"Project: {ROOT}",
        "",
        "=== GIT STATUS ===",
        run_git("status", "--short", "--branch"),
        "",
        "=== RECENT COMMITS ===",
        run_git("log", "-10", "--oneline"),
        "",
        "=== PROJECT FILES ===",
    ]

    files = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file() and should_include(path)
    )

    for path in files:
        sections.append(path.relative_to(ROOT).as_posix())

    sections.extend(["", "=== SOURCE CONTENTS ==="])

    for path in files:
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        sections.extend([
            "",
            f"--- FILE: {path.relative_to(ROOT).as_posix()} ---",
            content
        ])

    OUTPUT.write_text("\n".join(sections), encoding="utf-8")
    print(f"Snapshot created: {OUTPUT}")


if __name__ == "__main__":
    main()