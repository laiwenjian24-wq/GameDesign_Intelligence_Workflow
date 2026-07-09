"""Load lightweight continuity rules from project configuration."""

from json import JSONDecodeError, loads
from pathlib import Path
from typing import Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RULE_PATH = PROJECT_ROOT / "knowledge_base" / "continuity_rules" / "rules.json"


def load_continuity_rules(rule_path: Optional[Path] = None) -> List[Dict]:
    """Load enabled continuity rules from JSON configuration.

    Missing or invalid rule files degrade to no rules. The continuity checker
    can still produce a Context Pack report without project-specific checks.
    """
    path = rule_path or DEFAULT_RULE_PATH
    if not path.exists():
        return []

    try:
        data = loads(path.read_text(encoding="utf-8"))
    except (OSError, JSONDecodeError):
        return []

    rules = data.get("rules", [])
    if not isinstance(rules, list):
        return []

    return [rule for rule in rules if isinstance(rule, dict) and rule.get("enabled", True)]
