from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.types.exceptions import (
    APIException,
)


def create_exception_handler(
    status_code: int, initial_detail: str
) -> Callable[[Request, APIException], JSONResponse]:
    detail = {"message": initial_detail}

    async def exception_handler(_: Request, exc: APIException) -> JSONResponse:
        if exc.message:
            detail["message"] = exc.message

        if exc.name:
            detail["message"] = f"{detail['message']} [{exc.name}]"

        logger.error(exc)
        return JSONResponse(
            status_code=status_code, content={"detail": detail["message"]}
        )

    return exception_handler


# app.add_exception_handler(
#     exc_class_or_status_code=ExpiredSignatureError,
#     handler=create_exception_handler(
#         status.HTTP_401_UNAUTHORIZED, "Token has expired. Please log in again."
#     ),
# )
