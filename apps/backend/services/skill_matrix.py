"""Queries for the skill matrix and growth ledger."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Skill, SkillEvidence


def most_demonstrated_skills(db: Session, limit: int = 5) -> list[dict]:
    """Return skills with the most evidence entries."""
    rows = (
        db.query(Skill.name, func.count(SkillEvidence.id).label("evidence_count"))
        .join(SkillEvidence, SkillEvidence.skill_id == Skill.id)
        .group_by(Skill.id)
        .order_by(func.count(SkillEvidence.id).desc())
        .limit(limit)
        .all()
    )
    return [{"name": name, "evidence_count": count} for name, count in rows]


def skills_gap_vs_target_role(db: Session, targets: dict[int, int]) -> list[dict]:
    """Compare current skill levels against target role requirements.

    Parameters
    ----------
    db:
        Database session.
    targets:
        Mapping of ``skill_id`` to desired level for a role.
    """
    skills = db.query(Skill).filter(Skill.id.in_(targets.keys())).all()
    results: list[dict] = []
    for skill in skills:
        target_level = targets.get(skill.id, skill.level)
        results.append(
            {
                "skill_id": skill.id,
                "name": skill.name,
                "current_level": skill.level,
                "target_level": target_level,
                "gap": target_level - skill.level,
            }
        )
    return results
