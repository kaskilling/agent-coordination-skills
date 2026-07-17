#!/usr/bin/env python3
"""Validate the public agent-coordination skill collection without dependencies."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
LINK_RE = re.compile(r"\[[^]]*]\(([^)]+)\)")
PRIVATE_PATTERNS = (
    re.compile(r"/Users/[^/\s]+/"),
    re.compile(r"/home/[^/\s]+/"),
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
    re.compile(r"[A-Za-z0-9._%+-]+@agoda\.com", re.IGNORECASE),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        fail(errors, f"{path.relative_to(ROOT)}: missing opening frontmatter marker")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(errors, f"{path.relative_to(ROOT)}: missing closing frontmatter marker")
        return {}

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            fail(errors, f"{path.relative_to(ROOT)}: invalid frontmatter line {line!r}")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in values:
            fail(errors, f"{path.relative_to(ROOT)}: duplicate frontmatter key {key}")
        values[key] = value

    unexpected = sorted(set(values) - {"name", "description"})
    if unexpected:
        fail(errors, f"{path.relative_to(ROOT)}: unexpected frontmatter keys {unexpected}")
    return values


def validate_skill(skill_dir: Path, errors: list[str]) -> str | None:
    name = skill_dir.name
    rel = skill_dir.relative_to(ROOT)
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        fail(errors, f"{rel}: invalid skill directory name")

    skill_md = skill_dir / "SKILL.md"
    metadata = skill_dir / "agents" / "openai.yaml"
    if not skill_md.is_file():
        fail(errors, f"{rel}: missing SKILL.md")
        return None
    if not metadata.is_file():
        fail(errors, f"{rel}: missing agents/openai.yaml")

    values = parse_frontmatter(skill_md, errors)
    if values.get("name") != name:
        fail(errors, f"{rel}: frontmatter name must match directory name")
    description = values.get("description", "")
    if not description or len(description) > 1024:
        fail(errors, f"{rel}: description must contain 1-1024 characters")
    if "use when" not in description.lower():
        fail(errors, f"{rel}: description must say when to use the skill")

    content = skill_md.read_text(encoding="utf-8")
    if len(content.splitlines()) > 500:
        fail(errors, f"{rel}: SKILL.md exceeds 500 lines")
    if "TODO" in content:
        fail(errors, f"{rel}: unresolved TODO in SKILL.md")

    for target in LINK_RE.findall(content):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target_path = (skill_dir / target.split("#", 1)[0]).resolve()
        if not target_path.exists():
            fail(errors, f"{rel}: broken relative link {target}")

    if metadata.is_file():
        ui = metadata.read_text(encoding="utf-8")
        display = re.search(r'^\s*display_name:\s*"([^"]+)"\s*$', ui, re.MULTILINE)
        short = re.search(r'^\s*short_description:\s*"([^"]+)"\s*$', ui, re.MULTILINE)
        prompt = re.search(r'^\s*default_prompt:\s*"([^"]+)"\s*$', ui, re.MULTILINE)
        if not display:
            fail(errors, f"{rel}: missing quoted interface.display_name")
        if not short or not 25 <= len(short.group(1)) <= 64:
            fail(errors, f"{rel}: short_description must contain 25-64 characters")
        if not prompt or f"${name}" not in prompt.group(1):
            fail(errors, f"{rel}: default_prompt must explicitly mention ${name}")
    return name


def validate_inventory(skill_names: list[str], errors: list[str]) -> None:
    if len(skill_names) != len(set(skill_names)):
        fail(errors, "duplicate skill names detected")

    grouping = json.loads((ROOT / "skills.sh.json").read_text(encoding="utf-8"))
    grouped = [
        name
        for group in grouping.get("groupings", [])
        for name in group.get("skills", [])
    ]
    if set(grouped) != set(skill_names) or len(grouped) != len(skill_names):
        fail(errors, "skills.sh.json inventory must match skills/ exactly")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in skill_names:
        if f"skills/{name}/SKILL.md" not in readme:
            fail(errors, f"README.md: missing catalog link for {name}")

    manifest = json.loads(
        (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    allowed_manifest = {
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "skills",
        "interface",
    }
    unexpected = sorted(set(manifest) - allowed_manifest)
    if unexpected:
        fail(errors, f"plugin manifest contains unsupported fields {unexpected}")
    if manifest.get("name") != "agent-coordination-skills":
        fail(errors, "plugin name must be agent-coordination-skills")
    for field in ("description", "homepage", "repository", "license"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            fail(errors, f"plugin {field} must be a non-empty string")
    if manifest.get("skills") != "./skills/":
        fail(errors, "plugin skills path must be ./skills/")
    if not SEMVER_RE.fullmatch(str(manifest.get("version", ""))):
        fail(errors, "plugin version must use strict semantic versioning")
    for field in ("homepage", "repository"):
        parsed = urlparse(str(manifest.get(field, "")))
        if parsed.scheme != "https" or not parsed.netloc:
            fail(errors, f"plugin {field} must be an absolute HTTPS URL")

    author = manifest.get("author")
    if not isinstance(author, dict) or not isinstance(author.get("name"), str):
        fail(errors, "plugin author.name must be a non-empty string")
    elif not author["name"].strip():
        fail(errors, "plugin author.name must be a non-empty string")
    if isinstance(author, dict) and "url" in author:
        parsed = urlparse(str(author["url"]))
        if parsed.scheme != "https" or not parsed.netloc:
            fail(errors, "plugin author.url must be an absolute HTTPS URL")

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        fail(errors, "plugin interface must be an object")
    else:
        allowed_interface = {
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
            "capabilities",
            "websiteURL",
            "defaultPrompt",
        }
        unexpected = sorted(set(interface) - allowed_interface)
        if unexpected:
            fail(errors, f"plugin interface contains unsupported fields {unexpected}")
        for field in (
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
        ):
            value = interface.get(field)
            if not isinstance(value, str) or not value.strip():
                fail(errors, f"plugin interface.{field} must be a non-empty string")
        capabilities = interface.get("capabilities")
        if not isinstance(capabilities, list) or not all(
            isinstance(value, str) and value.strip() for value in capabilities
        ):
            fail(errors, "plugin interface.capabilities must be an array of strings")
        parsed = urlparse(str(interface.get("websiteURL", "")))
        if parsed.scheme != "https" or not parsed.netloc:
            fail(errors, "plugin interface.websiteURL must be an absolute HTTPS URL")
        prompts = interface.get("defaultPrompt")
        if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
            fail(errors, "plugin interface.defaultPrompt must contain 1-3 prompts")
        elif not all(
            isinstance(prompt, str) and 1 <= len(prompt) <= 128 for prompt in prompts
        ):
            fail(errors, "plugin default prompts must contain 1-128 characters")

    if "[TODO:" in json.dumps(manifest):
        fail(errors, "plugin manifest contains an unresolved TODO placeholder")


def validate_privacy(errors: list[str]) -> None:
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    for relative in completed.stdout.decode("utf-8").split("\0"):
        if not relative:
            continue
        path = ROOT / relative
        if not path.is_file():
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                fail(errors, f"{path.relative_to(ROOT)}: possible private path or email")


def main() -> int:
    errors: list[str] = []
    if not SKILLS_DIR.is_dir():
        fail(errors, "missing skills directory")
        skill_names: list[str] = []
    else:
        skill_names = [
            name
            for child in sorted(SKILLS_DIR.iterdir())
            if child.is_dir() and (name := validate_skill(child, errors))
        ]

    validate_inventory(skill_names, errors)
    validate_privacy(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_names)} skills: {', '.join(skill_names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
