from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.types.exceptions import APIException


def create_exception_handler(
    status_code: int, initial_detail: str
) -> Callable[[Request, APIException], JSONResponse]:
    detail = {'message': initial_detail}

    async def exception_handler(_: Request, exc: APIException) -> JSONResponse:
        if exc.message:
            detail['message'] = exc.message

        logger.error(f'{exc.__class__.__name__}: {exc.message}')
        return JSONResponse(
            status_code=status_code, content={'detail': detail['message']}
        )

    return exception_handler
