from fastapi import APIRouter, Depends

from app.api.deps import require_roles
from app.core.metrics import runtime_metrics
from app.models import User

router = APIRouter()


@router.get('/metrics')
def metrics(current_user: User = Depends(require_roles('admin'))) -> dict:
    return {'requested_by': current_user.id, 'metrics': runtime_metrics.snapshot()}
