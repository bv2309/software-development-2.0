from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ai_accel_api_platform.api.deps import get_db_session
from ai_accel_api_platform.core.schemas import ErrorResponse, UserFullNameResponse
from ai_accel_api_platform.core.security import decode_subject_from_token
from ai_accel_api_platform.core.utils import build_full_name
from ai_accel_api_platform.db.repositories import get_user_name_parts

router = APIRouter()

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/v1/auth/token", auto_error=False)


@router.get(
    "/user",
    response_model=UserFullNameResponse,
    responses={400: {"model": ErrorResponse}},
)
async def read_user_full_name(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    token: Annotated[str | None, Depends(oauth2_scheme_optional)],
) -> UserFullNameResponse | JSONResponse:
    try:
        if not token:
            raise ValueError("missing_token")

        username = decode_subject_from_token(token)
        record = await get_user_name_parts(session, username)
        if record is None:
            raise ValueError("user_not_found")

        first_name, last_name, is_active = record
        if not is_active:
            raise ValueError("user_inactive")

        full_name = build_full_name(first_name, last_name)
        return UserFullNameResponse(
            message="You've successfully fetched user object.",
            full_name=full_name,
        )
    except Exception:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(message="System failed to retrieve the data.").model_dump(),
        )
