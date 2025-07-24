"""
Experiment management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models.experiment import Experiment, Condition
from app.schemas.experiment import (
    ExperimentCreate,
    ExperimentUpdate,
    ExperimentResponse,
    ExperimentListResponse,
    ExperimentImportRequest,
    ExperimentValidationResponse,
    ConditionCreate,
    ConditionResponse
)
from typing import List, Optional
from uuid import UUID
import secrets
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=ExperimentListResponse)
async def list_experiments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all experiments with pagination"""
    query = select(Experiment).options(selectinload(Experiment.conditions))
    
    if search:
        query = query.where(
            Experiment.name.ilike(f"%{search}%") | 
            Experiment.description.ilike(f"%{search}%")
        )
    
    # Get total count
    count_query = select(func.count()).select_from(Experiment)
    if search:
        count_query = count_query.where(
            Experiment.name.ilike(f"%{search}%") | 
            Experiment.description.ilike(f"%{search}%")
        )
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Experiment.created_at.desc())
    
    result = await db.execute(query)
    experiments = result.scalars().all()
    
    return ExperimentListResponse(
        experiments=experiments,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create_experiment(
    experiment: ExperimentCreate,
    created_by: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Create a new experiment"""
    # Create experiment
    db_experiment = Experiment(
        name=experiment.name,
        description=experiment.description,
        config=experiment.config,
        version=experiment.version,
        created_by=created_by
    )
    db.add(db_experiment)
    await db.flush()
    
    # Create conditions from config if present
    conditions_config = experiment.config.get("conditions", [])
    for condition_data in conditions_config:
        access_code = secrets.token_urlsafe(8)
        db_condition = Condition(
            experiment_id=db_experiment.id,
            name=condition_data.get("name", "Default"),
            description=condition_data.get("description", ""),
            parameters=condition_data.get("parameters", {}),
            access_code=access_code
        )
        db.add(db_condition)
    
    await db.commit()
    await db.refresh(db_experiment)
    
    # Load conditions relationship
    await db.execute(
        select(Experiment)
        .options(selectinload(Experiment.conditions))
        .where(Experiment.id == db_experiment.id)
    )
    
    return db_experiment


@router.post("/import", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
async def import_experiment(
    import_request: ExperimentImportRequest,
    created_by: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Import experiment from YAML configuration"""
    try:
        config = import_request.validate_yaml()
        experiment = ExperimentCreate.from_yaml(import_request.yaml_content)
        return await create_experiment(experiment, created_by, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/validate", response_model=ExperimentValidationResponse)
async def validate_experiment(import_request: ExperimentImportRequest):
    """Validate experiment YAML configuration without creating it"""
    errors = []
    warnings = []
    parsed_config = None
    
    try:
        parsed_config = import_request.validate_yaml()
        
        # Validate scenario
        scenario = parsed_config.get("scenario", {})
        if not scenario.get("instructions"):
            errors.append("Missing scenario instructions")
        if not scenario.get("completionTrigger"):
            warnings.append("No completion trigger defined")
        
        # Validate roles
        roles = parsed_config.get("roles", [])
        if not roles:
            errors.append("No roles defined")
        else:
            human_count = sum(1 for r in roles if r.get("type") == "HUMAN")
            if human_count == 0:
                warnings.append("No human participants defined")
            
            for i, role in enumerate(roles):
                if not role.get("name"):
                    errors.append(f"Role {i} missing name")
                if role.get("type") == "AI" and not role.get("model"):
                    errors.append(f"AI role '{role.get('name', i)}' missing model")
        
        # Validate ethics if present
        ethics = parsed_config.get("ethics", {})
        if ethics.get("requiresConsent") and not ethics.get("consentFormPath"):
            warnings.append("Consent required but no consent form path provided")
        
        valid = len(errors) == 0
        
    except ValueError as e:
        errors.append(str(e))
        valid = False
    
    return ExperimentValidationResponse(
        valid=valid,
        errors=errors,
        warnings=warnings,
        parsed_config=parsed_config
    )


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get experiment details"""
    query = select(Experiment).options(selectinload(Experiment.conditions)).where(Experiment.id == experiment_id)
    result = await db.execute(query)
    experiment = result.scalar_one_or_none()
    
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    return experiment


@router.put("/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    experiment_id: UUID,
    experiment_update: ExperimentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an experiment"""
    query = select(Experiment).where(Experiment.id == experiment_id)
    result = await db.execute(query)
    experiment = result.scalar_one_or_none()
    
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    # Update fields if provided
    update_data = experiment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(experiment, field, value)
    
    await db.commit()
    await db.refresh(experiment)
    
    # Load conditions relationship
    await db.execute(
        select(Experiment)
        .options(selectinload(Experiment.conditions))
        .where(Experiment.id == experiment.id)
    )
    
    return experiment


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experiment(experiment_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete an experiment"""
    query = select(Experiment).where(Experiment.id == experiment_id)
    result = await db.execute(query)
    experiment = result.scalar_one_or_none()
    
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    await db.delete(experiment)
    await db.commit()


@router.get("/{experiment_id}/conditions", response_model=List[ConditionResponse])
async def list_experiment_conditions(experiment_id: UUID, db: AsyncSession = Depends(get_db)):
    """List all conditions for an experiment"""
    # Verify experiment exists
    exp_query = select(Experiment).where(Experiment.id == experiment_id)
    exp_result = await db.execute(exp_query)
    if not exp_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    # Get conditions
    query = select(Condition).where(Condition.experiment_id == experiment_id)
    result = await db.execute(query)
    conditions = result.scalars().all()
    
    return conditions


@router.post("/{experiment_id}/conditions", response_model=ConditionResponse, status_code=status.HTTP_201_CREATED)
async def create_condition(
    experiment_id: UUID,
    condition: ConditionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new condition for an experiment"""
    # Verify experiment exists
    exp_query = select(Experiment).where(Experiment.id == experiment_id)
    exp_result = await db.execute(exp_query)
    if not exp_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    # Create condition
    access_code = secrets.token_urlsafe(8)
    db_condition = Condition(
        experiment_id=experiment_id,
        name=condition.name,
        description=condition.description,
        parameters=condition.parameters,
        access_code=access_code
    )
    db.add(db_condition)
    await db.commit()
    await db.refresh(db_condition)
    
    return db_condition