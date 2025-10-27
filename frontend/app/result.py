from typing import Optional, Any

class Result:
    def __init__(self, success: bool, data: Optional[Any] = None, error: Optional[str] = None):
        self._success = success
        self._data = data
        self._error = error

    @classmethod
    def success(cls, data: Optional[Any] = None):
        return cls(success=True, data=data)

    @classmethod
    def failure(cls, error: str):
        return cls(success=False, error=error)

    def is_success(self) -> bool:
        return self._success

    def is_failure(self) -> bool:
        return not self._success

    @property
    def data(self) -> Optional[Any]:
        return self._data

    @property
    def error(self) -> Optional[str]:
        return self._error

    def __repr__(self):
        if self._success:
            return f"Result.success(data={self._data})"
        else:
            return f"Result.failure(error={self._error})"