# Integration Issues Tracker

This document tracks all integration issues discovered during testing phase.

## Issue #1: Missing aiosqlite dependency
- **Found**: 2025-07-24 16:45
- **Symptom**: Backend fails to start with `ModuleNotFoundError: No module named 'aiosqlite'`
- **Root Cause**: Dependency not installed despite being in requirements.txt
- **Fix**: `pip install aiosqlite==0.19.0`
- **Status**: ✅ Fixed
- **Lesson**: Need setup instructions to install all dependencies

## Issue #2: SQLAlchemy reserved word conflict
- **Found**: 2025-07-24 16:47
- **Symptom**: Backend fails with `InvalidRequestError: Attribute name 'metadata' is reserved`
- **Root Cause**: Message model used 'metadata' as column name, which is reserved in SQLAlchemy
- **Fix**: Renamed to 'message_metadata' in app/models/message.py
- **Status**: ✅ Fixed
- **Lesson**: Avoid SQLAlchemy reserved words (metadata, query, etc.)

## Issue #3: Incorrect API base URL in test script
- **Found**: 2025-07-24 16:52
- **Symptom**: Test script fails with 404 Not Found for experiments endpoint
- **Root Cause**: Test script used `/api/v1` but backend uses `/api`
- **Fix**: Changed API_BASE_URL from `http://localhost:8000/api/v1` to `http://localhost:8000/api`
- **Status**: ✅ Fixed
- **Lesson**: Always verify actual API routes before hardcoding URLs

## Issue #4: Frontend port not in CORS allowed origins
- **Found**: 2025-07-24 17:00
- **Symptom**: Frontend on port 5173 might have CORS issues
- **Root Cause**: CORS settings only allowed ports 8080 and 3000
- **Fix**: Added http://localhost:5173 to CORS_ORIGINS in config.py
- **Status**: ✅ Fixed (preventative)
- **Lesson**: Update CORS settings to match actual frontend port

## Issue #5: Pydantic validation error - updated_at field
- **Found**: 2025-07-24 17:05
- **Symptom**: GET /api/experiments/ returns 500 due to validation error
- **Root Cause**: Schema expects datetime but database returns None for updated_at
- **Fix**: Made updated_at Optional[datetime] in ExperimentResponse schema
- **Status**: ✅ Fixed
- **Lesson**: Database nullable fields must be Optional in Pydantic schemas

## Issue #6: Session creation API mismatch
- **Found**: 2025-07-24 17:10
- **Symptom**: 422 Unprocessable Entity when creating session
- **Root Cause**: Test script sending wrong fields (experiment_id, planned_duration_minutes)
- **Fix**: Updated to send correct fields (condition_id, team_size, required_humans)
- **Status**: ✅ Fixed
- **Lesson**: Always check actual API schemas, not assumptions

## Issue #7: Trailing slash requirement for all endpoints
- **Found**: 2025-07-24 17:15
- **Symptom**: 404 errors on valid endpoints, 307 redirects
- **Root Cause**: FastAPI requires trailing slashes on all endpoints
- **Fix**: Added trailing slashes to all API calls in test script
- **Status**: ✅ Fixed
- **Lesson**: FastAPI is strict about trailing slashes - always include them

## Issue #8: UUID to String conversion in database queries
- **Found**: 2025-07-24 17:20
- **Symptom**: GET /api/experiments/{id} returns 404 even though experiment exists
- **Root Cause**: Database stores IDs as strings but queries compared UUID directly
- **Fix**: Added str() conversion to all experiment_id comparisons in queries
- **Status**: ✅ Fixed
- **Lesson**: Always convert UUIDs to strings when querying string ID columns

## Issue #9: Pervasive UUID to String conversion needed
- **Found**: 2025-07-24 17:25
- **Symptom**: Multiple 500 errors with "type 'UUID' is not supported" 
- **Root Cause**: SQLite doesn't support UUID type, all IDs stored as strings
- **Fix**: Converting UUIDs to strings in all db.get() calls and foreign key assignments
- **Status**: 🔄 In Progress (fixing as we find them)
- **Lesson**: When using SQLite, consistently use string IDs throughout

## Issue #10: Enum value mismatch between model and schema
- **Found**: 2025-07-24 17:30
- **Symptom**: ResponseValidationError - enum expects uppercase but gets lowercase
- **Root Cause**: Model defined SessionStatus with lowercase values, schema expects uppercase
- **Fix**: Changed model SessionStatus enum to use uppercase values
- **Status**: ✅ Fixed
- **Lesson**: Ensure enum values match exactly between models and schemas

## Issue #11: Participants API not implemented
- **Found**: 2025-07-24 17:35
- **Symptom**: 404 Not Found on POST /api/participants/
- **Root Cause**: Participants API has placeholder endpoints only
- **Fix**: Need to implement actual participant creation endpoint
- **Status**: 🔴 Blocking - API not implemented
- **Lesson**: Check if APIs are actually implemented, not just defined

## Summary So Far

### Critical Issues Found:
1. Missing dependencies not automatically installed (aiosqlite)
2. SQLAlchemy reserved word conflicts (metadata)
3. API endpoint paths mismatch (missing /v1, trailing slashes required)
4. UUID to String conversion needed throughout (SQLite limitation)
5. Schema/Model mismatches (enum values, optional fields)
6. **Participants API not implemented** (placeholder code only)

### Progress Made:
- ✅ Fixed dependency issues
- ✅ Fixed database field conflicts
- ✅ Fixed API path issues
- ✅ Fixed many UUID conversion issues
- ✅ Fixed enum mismatches
- ✅ Successfully created experiment and session!
- ❌ Blocked on participants API

### Key Takeaways:
- **Agent-950 was absolutely right** - test integration before adding features!
- Many issues only surface during actual integration testing
- SQLite has limitations (no UUID support) that affect entire codebase
- Schema/Model consistency is critical
- Always verify APIs are actually implemented, not just stubbed