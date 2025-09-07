from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..db import get_db
from .services import models, skill_matrix

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=List[schemas.SkillOut])
def list_skills(db: Session = Depends(get_db)):
    return db.query(models.Skill).all()


@router.post("/", response_model=schemas.SkillOut)
def create_skill(skill: schemas.SkillCreate, db: Session = Depends(get_db)):
    db_skill = models.Skill(**skill.dict())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


@router.get("/{skill_id}/evidence", response_model=List[schemas.SkillEvidenceOut])
def skill_evidence(skill_id: int, db: Session = Depends(get_db)):
    return db.query(models.SkillEvidence).filter_by(skill_id=skill_id).all()


@router.post("/evidence", response_model=schemas.SkillEvidenceOut)
def add_evidence(evidence: schemas.SkillEvidenceCreate, db: Session = Depends(get_db)):
    db_e = models.SkillEvidence(**evidence.dict())
    db.add(db_e)
    db.commit()
    db.refresh(db_e)
    return db_e


@router.get("/learning-goals", response_model=List[schemas.LearningGoalOut])
def list_goals(db: Session = Depends(get_db)):
    return db.query(models.LearningGoal).all()


@router.post("/learning-goals", response_model=schemas.LearningGoalOut)
def create_goal(goal: schemas.LearningGoalCreate, db: Session = Depends(get_db)):
    db_goal = models.LearningGoal(**goal.dict())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.get("/most-demonstrated", response_model=List[schemas.SkillStats])
def most_demonstrated(limit: int = 5, db: Session = Depends(get_db)):
    return skill_matrix.most_demonstrated_skills(db, limit)


@router.post("/gap", response_model=List[schemas.SkillGap])
def skills_gap(targets: Dict[int, int], db: Session = Depends(get_db)):
    return skill_matrix.skills_gap_vs_target_role(db, targets)
