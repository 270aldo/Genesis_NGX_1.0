#!/usr/bin/env python3
"""
Script to sanitize sensitive information from logs.
This script finds and replaces sensitive log statements with sanitized versions.
"""

import re
from pathlib import Path
from typing import List, Tuple

# Patterns to identify sensitive logs
SENSITIVE_PATTERNS = [
    # Pattern, Replacement
    (
        r'logger\.(debug|info|warning|error)\(f"(.*?)user_id: \{user_id\}(.*?)"\)',
        r'logger.\1(f"\2user_id: [REDACTED]\3")',
    ),
    (
        r'logger\.(debug|info|warning|error)\(f"(.*?)user \{user_id\}(.*?)"\)',
        r'logger.\1(f"\2user [REDACTED]\3")',
    ),
    (
        r'logger\.(debug|info|warning|error)\(f"(.*?)token: \{[^}]+\}(.*?)"\)',
        r'logger.\1(f"\2token: [REDACTED]\3")',
    ),
    (
        r'logger\.(debug|info|warning|error)\(f"(.*?)password: \{[^}]+\}(.*?)"\)',
        r'logger.\1(f"\2password: [REDACTED]\3")',
    ),
    (
        r'logger\.(debug|info|warning|error)\(f"(.*?)api_key: \{[^}]+\}(.*?)"\)',
        r'logger.\1(f"\2api_key: [REDACTED]\3")',
    ),
]

# Use hash for user tracking instead of direct ID
HASH_PATTERN = (
    r'logger\.(debug|info|warning|error)\(f"(.*?)user_id: \{user_id\}(.*?)"\)'
)
HASH_REPLACEMENT = r'logger.\1(f"\2user_hash: {hashlib.sha256(str(user_id).encode()).hexdigest()[:8]}\3")'


def sanitize_file(file_path: Path, dry_run: bool = True) -> List[Tuple[int, str, str]]:
    """
    Sanitize sensitive information in a single file.

    Args:
        file_path: Path to the file to sanitize
        dry_run: If True, only report changes without modifying files

    Returns:
        List of (line_number, original, replacement) tuples
    """
    changes = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return changes

    modified_lines = []
    for i, line in enumerate(lines, 1):
        original_line = line
        modified = False

        # Check each sensitive pattern
        for pattern, replacement in SENSITIVE_PATTERNS:
            if re.search(pattern, line):
                new_line = re.sub(pattern, replacement, line)
                if new_line != line:
                    line = new_line
                    modified = True

        if modified:
            changes.append((i, original_line, line))

        modified_lines.append(line)

    # Write changes if not dry run
    if changes and not dry_run:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(modified_lines))
            print(f"✅ Modified {file_path}: {len(changes)} changes")
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")

    return changes


def find_python_files(root_dir: Path, exclude_dirs: List[str] = None) -> List[Path]:
    """Find all Python files in the project."""
    if exclude_dirs is None:
        exclude_dirs = ["venv", "__pycache__", ".git", "node_modules", "dist", "build"]

    python_files = []
    for path in root_dir.rglob("*.py"):
        # Skip excluded directories
        if any(excluded in path.parts for excluded in exclude_dirs):
            continue
        python_files.append(path)

    return python_files


def main():
    """Main function to sanitize all Python files in the backend."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sanitize sensitive information from logs"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would be changed without modifying files",
    )
    parser.add_argument(
        "--path",
        default="/Users/aldoolivas/Desktop/NGX_Ecosystem/GENESIS_oficial_BETA/backend",
        help="Path to backend directory",
    )
    args = parser.parse_args()

    root_dir = Path(args.path)
    if not root_dir.exists():
        print(f"❌ Directory not found: {root_dir}")
        return 1

    print(f"🔍 Scanning for Python files in {root_dir}")
    python_files = find_python_files(root_dir)
    print(f"📁 Found {len(python_files)} Python files")

    total_changes = 0
    files_with_changes = 0

    for file_path in python_files:
        changes = sanitize_file(file_path, dry_run=args.dry_run)
        if changes:
            files_with_changes += 1
            total_changes += len(changes)

            if args.dry_run:
                print(f"\n📄 {file_path.relative_to(root_dir)}")
                for line_num, original, replacement in changes[
                    :3
                ]:  # Show first 3 changes
                    print(f"  Line {line_num}:")
                    print(f"    - {original.strip()}")
                    print(f"    + {replacement.strip()}")
                if len(changes) > 3:
                    print(f"  ... and {len(changes) - 3} more changes")

    print("\n📊 Summary:")
    print(f"  Files with sensitive logs: {files_with_changes}")
    print(f"  Total changes needed: {total_changes}")

    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes")
    else:
        print("\n✅ Sanitization complete!")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
