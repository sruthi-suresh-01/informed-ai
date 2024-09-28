from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import VARCHAR, TypeDecorator

PydanticData = BaseModel | list[BaseModel]


class EnumAsString(TypeDecorator):
    impl = VARCHAR

    # added this to avoid warnings from SQLAlchemy
    # set to False since we are using this type in state machines
    cache_ok = False

    def __init__(self, enumtype: type[Enum], *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value: Enum | str | None, dialect: Dialect) -> Any:
        if value is None:
            return None
        if isinstance(value, Enum):
            return value.value
        elif isinstance(value, str):
            return self._enumtype(value).value

    def process_result_value(self, value: str | None, dialect: Dialect) -> Enum | None:
        if value is None:
            return None
        return self._enumtype(value)


class JSONBFromPydantic(TypeDecorator):
    impl = JSONB

    # added this to avoid warnings from SQLAlchemy
    # set to False since this might invlove state machines
    cache_ok = False

    def __init__(self, pydantic_type: type[BaseModel], *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.pydantic_type = pydantic_type

    def process_bind_param(
        self, value: PydanticData | None, dialect: Dialect
    ) -> dict | list | None:
        if value is not None:
            if isinstance(value, list):
                return [obj.model_dump(mode="json") for obj in value]
            else:
                return value.model_dump(mode="json")
        return None

    def process_result_value(
        self, value: dict | list | None, dialect: Dialect
    ) -> PydanticData | None:
        if value is not None:
            if isinstance(value, list):
                return [self.pydantic_type.model_validate(item) for item in value]
            else:
                return self.pydantic_type.model_validate(value)
        return None
