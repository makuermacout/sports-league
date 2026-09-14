from fastapi import HTTPException, status


class ApiError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(status_code=status_code, detail={"code": code, "message": message})
        self.code = code
        self.message = message


def validation_error(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> ApiError:
    return ApiError(status_code, "validation_error", message)


def duplicate_team() -> ApiError:
    return ApiError(
        status.HTTP_409_CONFLICT,
        "duplicate_team",
        "A team with this name already exists in the league.",
    )


def team_not_found() -> ApiError:
    return ApiError(
        status.HTTP_404_NOT_FOUND,
        "team_not_found",
        "One or both teams do not exist in the league.",
    )


def same_team() -> ApiError:
    return ApiError(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "same_team",
        "A match must be between two different teams.",
    )
