---
mode: ask
description: Add a new REST API endpoint with Pydantic models, service, and router
---

# Add API Endpoint

Create a new REST API endpoint following CoreAI DIY patterns.

## Variables

- `RESOURCE_NAME`: The resource name (singular, e.g., `annotation`)
- `RESOURCE_PLURAL`: Plural form (e.g., `annotations`)
- `RESOURCE_DESCRIPTION`: Brief description
- `RESOURCE_FIELDS`: Key fields for the resource

## Steps

### 1. Define Pydantic Models

Create `src/backend/app/models/${RESOURCE_NAME}.py`:

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ${RESOURCE_NAME.title()}Base(BaseModel):
    """Base model with common fields."""
    # Add ${RESOURCE_FIELDS}
    
    class Config:
        populate_by_name = True

class ${RESOURCE_NAME.title()}Create(${RESOURCE_NAME.title()}Base):
    """Request model for creation."""
    # Add required creation fields
    pass

class ${RESOURCE_NAME.title()}Update(BaseModel):
    """Request model for partial updates (all optional)."""
    # Add optional update fields
    pass

class ${RESOURCE_NAME.title()}(${RESOURCE_NAME.title()}Base):
    """Response model."""
    id: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    
    class Config:
        from_attributes = True
        populate_by_name = True

class ${RESOURCE_NAME.title()}InDB(${RESOURCE_NAME.title()}):
    """Database document model."""
    doc_type: str = "${RESOURCE_NAME}"
```

### 2. Create Service

Create `src/backend/app/services/${RESOURCE_NAME}_service.py`:

```python
from typing import Optional
from app.db.cosmos import get_container, query_documents, upsert_document
from app.models.${RESOURCE_NAME} import ${RESOURCE_NAME.title()}, ${RESOURCE_NAME.title()}Create

class ${RESOURCE_NAME.title()}Service:
    def _use_cosmos(self) -> bool:
        return get_container() is not None
    
    async def get_${RESOURCE_NAME}_by_id(
        self, ${RESOURCE_NAME}_id: str
    ) -> Optional[${RESOURCE_NAME.title()}]:
        if self._use_cosmos():
            docs = await query_documents(
                doc_type="${RESOURCE_NAME}",
                extra_filter="AND c.id = @id",
                parameters=[{"name": "@id", "value": ${RESOURCE_NAME}_id}],
            )
            return self._doc_to_${RESOURCE_NAME}(docs[0]) if docs else None
        return None
    
    async def create_${RESOURCE_NAME}(
        self, data: ${RESOURCE_NAME.title()}Create, user_id: str
    ) -> ${RESOURCE_NAME.title()}:
        # Implementation
        pass
    
    def _doc_to_${RESOURCE_NAME}(self, doc: dict) -> ${RESOURCE_NAME.title()}:
        return ${RESOURCE_NAME.title()}(**doc)
```

### 3. Create Router

Create `src/backend/app/routers/${RESOURCE_PLURAL}.py`:

```python
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.jwt import get_current_user, get_current_user_required
from app.models.user import User
from app.models.${RESOURCE_NAME} import (
    ${RESOURCE_NAME.title()},
    ${RESOURCE_NAME.title()}Create,
    ${RESOURCE_NAME.title()}Update,
)
from app.services.${RESOURCE_NAME}_service import ${RESOURCE_NAME.title()}Service

router = APIRouter(prefix="/api", tags=["${RESOURCE_PLURAL}"])

@router.get("/${RESOURCE_PLURAL}/{${RESOURCE_NAME}_id}", response_model=${RESOURCE_NAME.title()})
async def get_${RESOURCE_NAME}(
    ${RESOURCE_NAME}_id: str,
    current_user: Optional[User] = Depends(get_current_user),
) -> ${RESOURCE_NAME.title()}:
    """Get ${RESOURCE_NAME} by ID."""
    service = ${RESOURCE_NAME.title()}Service()
    result = await service.get_${RESOURCE_NAME}_by_id(${RESOURCE_NAME}_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return result

@router.post("/${RESOURCE_PLURAL}", status_code=status.HTTP_201_CREATED)
async def create_${RESOURCE_NAME}(
    data: ${RESOURCE_NAME.title()}Create,
    current_user: User = Depends(get_current_user_required),
) -> ${RESOURCE_NAME.title()}:
    """Create new ${RESOURCE_NAME}."""
    service = ${RESOURCE_NAME.title()}Service()
    return await service.create_${RESOURCE_NAME}(data, current_user.id)

@router.patch("/${RESOURCE_PLURAL}/{${RESOURCE_NAME}_id}")
async def update_${RESOURCE_NAME}(
    ${RESOURCE_NAME}_id: str,
    data: ${RESOURCE_NAME.title()}Update,
    current_user: User = Depends(get_current_user_required),
) -> ${RESOURCE_NAME.title()}:
    """Update ${RESOURCE_NAME}."""
    # Implementation
    pass

@router.delete("/${RESOURCE_PLURAL}/{${RESOURCE_NAME}_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_${RESOURCE_NAME}(
    ${RESOURCE_NAME}_id: str,
    current_user: User = Depends(get_current_user_required),
) -> None:
    """Delete ${RESOURCE_NAME}."""
    # Implementation
    pass
```

### 4. Mount Router

In `src/backend/app/main.py`:

```python
from app.routers.${RESOURCE_PLURAL} import router as ${RESOURCE_PLURAL}_router
app.include_router(${RESOURCE_PLURAL}_router)
```

### 5. Add Frontend Types

In `src/frontend/src/types/index.ts`:

```typescript
export interface ${RESOURCE_NAME.title()} {
  id: string;
  // Add fields
  createdAt: string;
  updatedAt?: string;
}

export interface ${RESOURCE_NAME.title()}Create {
  // Add creation fields
}
```

### 6. Add API Functions

In `src/frontend/src/services/api.ts`:

```typescript
export async function get${RESOURCE_NAME.title()}(id: string): Promise<${RESOURCE_NAME.title()}> {
  return authFetch(`/api/${RESOURCE_PLURAL}/${id}`);
}

export async function create${RESOURCE_NAME.title()}(data: ${RESOURCE_NAME.title()}Create): Promise<${RESOURCE_NAME.title()}> {
  return authFetch('/api/${RESOURCE_PLURAL}', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
```

## Checklist

- [ ] Pydantic models (Base, Create, Update, Response, InDB)
- [ ] Service with Cosmos DB integration
- [ ] Router with auth dependencies
- [ ] Router mounted in main.py
- [ ] Frontend types
- [ ] API client functions
- [ ] Tests added
