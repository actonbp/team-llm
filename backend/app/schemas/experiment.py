"""
Pydantic schemas for Experiment-related operations
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import yaml


class ConditionBase(BaseModel):
    """Base schema for experimental conditions"""
    name: str = Field(..., description="Condition name")
    description: str = Field(..., description="Condition description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Condition-specific parameters")


class ConditionCreate(ConditionBase):
    """Schema for creating a condition"""
    pass


class ConditionResponse(ConditionBase):
    """Schema for condition responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    experiment_id: UUID
    access_code: str
    created_at: datetime


class ExperimentBase(BaseModel):
    """Base schema for experiments"""
    name: str = Field(..., min_length=1, description="Experiment name")
    description: Optional[str] = Field(None, description="Experiment description")
    version: int = Field(default=1, ge=1, description="Experiment version")


class ExperimentCreate(ExperimentBase):
    """Schema for creating an experiment from YAML"""
    config: Dict[str, Any] = Field(..., description="Full experiment configuration")
    
    @classmethod
    def from_yaml(cls, yaml_content: str) -> "ExperimentCreate":
        """Create from YAML configuration file"""
        config = yaml.safe_load(yaml_content)
        return cls(
            name=config.get("experimentName", "Unnamed Experiment"),
            description=config.get("description", ""),
            version=config.get("version", 1),
            config=config
        )


class ExperimentUpdate(BaseModel):
    """Schema for updating an experiment"""
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ExperimentResponse(ExperimentBase):
    """Schema for experiment responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    config: Dict[str, Any]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    conditions: List[ConditionResponse] = []


class ExperimentListResponse(BaseModel):
    """Schema for listing experiments"""
    experiments: List[ExperimentResponse]
    total: int
    page: int = 1
    page_size: int = 20


class ExperimentImportRequest(BaseModel):
    """Schema for importing experiment from YAML"""
    yaml_content: str = Field(..., description="YAML configuration content")
    
    def validate_yaml(self) -> Dict[str, Any]:
        """Validate and parse YAML content"""
        try:
            config = yaml.safe_load(self.yaml_content)
            # Validate required fields
            required_fields = ["experimentName", "scenario", "roles"]
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field: {field}")
            return config
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {str(e)}")


class ExperimentValidationResponse(BaseModel):
    """Schema for experiment validation results"""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    parsed_config: Optional[Dict[str, Any]] = None