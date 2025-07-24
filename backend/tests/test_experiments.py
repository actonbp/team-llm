"""
Tests for Experiment API endpoints
"""
import pytest
from uuid import uuid4
from datetime import datetime


class TestExperimentAPI:
    """Test cases for experiment endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_experiment(self, client, sample_experiment_data):
        """Test creating a new experiment"""
        response = client.post(
            "/api/experiments/",
            json=sample_experiment_data,
            params={"created_by": "test_researcher"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_experiment_data["name"]
        assert data["description"] == sample_experiment_data["description"]
        assert data["version"] == sample_experiment_data["version"]
        assert data["created_by"] == "test_researcher"
        assert "id" in data
        assert "created_at" in data
        assert data["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_import_experiment_from_yaml(self, client, sample_experiment_yaml):
        """Test importing experiment from YAML"""
        response = client.post(
            "/api/experiments/import",
            json={
                "yaml_content": sample_experiment_yaml,
                "validate_only": False
            },
            params={"created_by": "test_researcher"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Trust Building Exercise"
        assert data["description"] == "A collaborative problem-solving task to study trust dynamics"
        assert data["version"] == 1
        assert len(data["config"]["conditions"]) == 2
        assert data["config"]["conditions"][0]["id"] == "baseline"
    
    @pytest.mark.asyncio
    async def test_validate_experiment_yaml(self, client, sample_experiment_yaml):
        """Test validating experiment YAML without creating"""
        response = client.post(
            "/api/experiments/import",
            json={
                "yaml_content": sample_experiment_yaml,
                "validate_only": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["name"] == "Trust Building Exercise"
        assert "warnings" in data
    
    @pytest.mark.asyncio
    async def test_validate_invalid_yaml(self, client):
        """Test validating invalid YAML"""
        invalid_yaml = """
experimentName: "Invalid Experiment"
# Missing required fields like roles and conditions
"""
        response = client.post(
            "/api/experiments/import",
            json={
                "yaml_content": invalid_yaml,
                "validate_only": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True  # Basic structure is valid
        assert len(data["warnings"]) > 0  # But has warnings about missing fields
    
    @pytest.mark.asyncio
    async def test_get_experiment(self, client, sample_experiment_data):
        """Test retrieving a single experiment"""
        # First create an experiment
        create_response = client.post(
            "/api/experiments/",
            json=sample_experiment_data
        )
        experiment_id = create_response.json()["id"]
        
        # Then retrieve it
        response = client.get(f"/api/experiments/{experiment_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == experiment_id
        assert data["name"] == sample_experiment_data["name"]
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_experiment(self, client):
        """Test retrieving non-existent experiment"""
        fake_id = str(uuid4())
        response = client.get(f"/api/experiments/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_list_experiments(self, client, sample_experiment_data):
        """Test listing experiments with pagination"""
        # Create multiple experiments
        for i in range(3):
            data = sample_experiment_data.copy()
            data["name"] = f"Test Experiment {i}"
            client.post("/api/experiments/", json=data)
        
        # Test pagination
        response = client.get("/api/experiments/", params={"skip": 0, "limit": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 3
        assert data["skip"] == 0
        assert data["limit"] == 2
    
    @pytest.mark.asyncio
    async def test_search_experiments(self, client, sample_experiment_data):
        """Test searching experiments by name"""
        # Create experiments with different names
        for name in ["Alpha Experiment", "Beta Test", "Alpha Protocol"]:
            data = sample_experiment_data.copy()
            data["name"] = name
            client.post("/api/experiments/", json=data)
        
        # Search for "Alpha"
        response = client.get("/api/experiments/", params={"search": "Alpha"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all("Alpha" in item["name"] for item in data["items"])
    
    @pytest.mark.asyncio
    async def test_filter_experiments_by_status(self, client, sample_experiment_data):
        """Test filtering experiments by active status"""
        # Create active experiment
        client.post("/api/experiments/", json=sample_experiment_data)
        
        # Create and then deactivate an experiment
        create_response = client.post(
            "/api/experiments/",
            json={**sample_experiment_data, "name": "Inactive Experiment"}
        )
        inactive_id = create_response.json()["id"]
        client.put(f"/api/experiments/{inactive_id}", json={"is_active": False})
        
        # Filter active only
        response = client.get("/api/experiments/", params={"is_active": True})
        assert response.status_code == 200
        data = response.json()
        assert all(item["is_active"] for item in data["items"])
        
        # Filter inactive only
        response = client.get("/api/experiments/", params={"is_active": False})
        assert response.status_code == 200
        data = response.json()
        assert all(not item["is_active"] for item in data["items"])
    
    @pytest.mark.asyncio
    async def test_update_experiment(self, client, sample_experiment_data):
        """Test updating an experiment"""
        # Create experiment
        create_response = client.post("/api/experiments/", json=sample_experiment_data)
        experiment_id = create_response.json()["id"]
        
        # Update it
        update_data = {
            "name": "Updated Experiment Name",
            "description": "Updated description",
            "version": 2
        }
        response = client.put(f"/api/experiments/{experiment_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["version"] == update_data["version"]
        assert data["updated_at"] is not None
    
    @pytest.mark.asyncio
    async def test_delete_experiment(self, client, sample_experiment_data):
        """Test deleting an experiment"""
        # Create experiment
        create_response = client.post("/api/experiments/", json=sample_experiment_data)
        experiment_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/experiments/{experiment_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/api/experiments/{experiment_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_experiment_conditions(self, client, sample_experiment_yaml):
        """Test retrieving experiment conditions"""
        # Import experiment with conditions
        import_response = client.post(
            "/api/experiments/import",
            json={"yaml_content": sample_experiment_yaml}
        )
        experiment_id = import_response.json()["id"]
        
        # Get conditions
        response = client.get(f"/api/experiments/{experiment_id}/conditions")
        assert response.status_code == 200
        conditions = response.json()
        assert len(conditions) == 2
        assert conditions[0]["condition_id"] == "baseline"
        assert conditions[0]["name"] == "Baseline Condition"
        assert conditions[1]["condition_id"] == "high-trust"
    
    @pytest.mark.asyncio
    async def test_get_experiment_statistics(self, client, sample_experiment_data):
        """Test retrieving experiment statistics"""
        # Create experiment
        create_response = client.post("/api/experiments/", json=sample_experiment_data)
        experiment_id = create_response.json()["id"]
        
        # Get statistics (should be empty for new experiment)
        response = client.get(f"/api/experiments/{experiment_id}/statistics")
        assert response.status_code == 200
        stats = response.json()
        assert stats["experiment_id"] == experiment_id
        assert stats["total_sessions"] == 0
        assert stats["active_sessions"] == 0
        assert stats["completed_sessions"] == 0
        assert stats["total_participants"] == 0
        assert stats["sessions_by_condition"] == {}
    
    @pytest.mark.asyncio
    async def test_create_experiment_missing_fields(self, client):
        """Test creating experiment with missing required fields"""
        response = client.post(
            "/api/experiments/",
            json={"name": "Incomplete Experiment"}
        )
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_experiment_yaml_with_ai_agents(self, client):
        """Test importing experiment with AI agent configuration"""
        yaml_with_ai = """
experimentName: "Human-AI Collaboration Study"
description: "Study collaboration patterns"
version: 1
roles:
  - name: "Participant"
    type: "human"
    instructions: "Work with the AI assistant"
  - name: "Assistant Alpha"
    type: "AI"
    model: "gpt-4"
    persona: "You are helpful and knowledgeable"
    knowledge:
      domain: "problem solving"
      expertise: ["logic", "mathematics"]
    strategy: "Guide without giving direct answers"
  - name: "Assistant Beta"
    type: "AI"
    model: "claude-3"
    persona: "You are creative and encouraging"
    knowledge:
      domain: "creative thinking"
    strategy: "Inspire creative solutions"
scenario:
  type: "collaborative"
  duration: 1200
conditions:
  - id: "single-ai"
    name: "Single AI Assistant"
    description: "One AI partner"
    variables:
      active_ai: ["Assistant Alpha"]
  - id: "dual-ai"
    name: "Dual AI Assistants"
    description: "Two AI partners"
    variables:
      active_ai: ["Assistant Alpha", "Assistant Beta"]
"""
        
        response = client.post(
            "/api/experiments/import",
            json={"yaml_content": yaml_with_ai}
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["config"]["roles"]) == 3
        assert sum(1 for r in data["config"]["roles"] if r["type"] == "AI") == 2