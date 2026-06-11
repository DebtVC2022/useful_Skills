from __future__ import annotations

from dataclasses import dataclass
import re


REQUIREMENT_ID_PATTERN = r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+"
REQUIREMENT_HEADING = re.compile(
    rf"^### Requirement:\s+({REQUIREMENT_ID_PATTERN})\s+(.+?)\s*$",
    re.MULTILINE,
)
DELTA_HEADING = re.compile(
    r"^## (ADDED|MODIFIED|REMOVED) Requirements\s*$",
    re.MULTILINE,
)
SCENARIO_HEADING = re.compile(r"^#### Scenario:\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    title: str
    content: str
    scenarios: tuple[str, ...]
    operation: str | None = None


def _requirements_in_block(block: str, operation: str | None) -> list[Requirement]:
    matches = list(REQUIREMENT_HEADING.finditer(block))
    requirements: list[Requirement] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(block)
        content = block[match.end() : end].strip()
        scenarios = tuple(SCENARIO_HEADING.findall(content))
        requirements.append(
            Requirement(
                requirement_id=match.group(1),
                title=match.group(2).strip(),
                content=content,
                scenarios=scenarios,
                operation=operation,
            )
        )
    return requirements


def parse_delta_spec(text: str) -> list[Requirement]:
    headings = list(DELTA_HEADING.finditer(text))
    requirements: list[Requirement] = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        block = text[heading.end() : end]
        requirements.extend(_requirements_in_block(block, heading.group(1)))
    return requirements


def parse_baseline_spec(text: str) -> dict[str, Requirement]:
    return {
        requirement.requirement_id: requirement
        for requirement in _requirements_in_block(text, None)
    }


def requirement_ids(text: str) -> set[str]:
    return set(re.findall(REQUIREMENT_ID_PATTERN, text))


def has_given_when_then(text: str) -> bool:
    upper = text.upper()
    return (
        re.search(r"(?m)^\s*-\s*GIVEN\b", upper) is not None
        and re.search(r"(?m)^\s*-\s*WHEN\b", upper) is not None
        and re.search(r"(?m)^\s*-\s*THEN\b", upper) is not None
    )
