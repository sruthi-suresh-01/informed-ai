from informed.db_models.query import Query, QueryState
from uuid import UUID
from informed.db import session_maker
from sqlalchemy.sql import select, ColumnElement
from typing import cast
from informed.api.api_types import UpdateQueryRequest, QueryResponse


class QueryManager:
    def __init__(self) -> None:
        # self.queries: dict[UUID, Query] = {}
        pass

    async def create_query(self, user_id: UUID, query: str) -> QueryResponse:
        created_query = Query(user_id=user_id, query=query)
        async with session_maker() as session:
            session.add(created_query)
            await session.commit()
        return QueryResponse.from_db(created_query)

    async def persist_query(self, query: Query) -> None:
        async with session_maker() as session:
            session.add(query)
            await session.commit()

    async def get_query(self, query_id: UUID) -> Query | None:
        async with session_maker() as session:
            query = await session.execute(
                select(Query)
                .filter(cast(ColumnElement[bool], Query.query_id == query_id))
                .with_for_update()
            )
            return query.scalar_one_or_none()

    async def update_query(self, request: UpdateQueryRequest) -> QueryResponse:
        async with session_maker() as session:
            statement = (
                select(Query)
                .filter(cast(ColumnElement[bool], Query.query_id == request.query_id))
                .with_for_update()
            )
            result = await session.execute(statement)
            db_query = result.scalar_one_or_none()
            if db_query is None:
                raise ValueError(f"Query {request.query_id} not found")
            db_query.state = request.state
            session.add(db_query)
            await session.commit()
            return QueryResponse.from_db(db_query)

    async def get_recent_query_for_user(self, user_id: UUID) -> Query | None:
        async with session_maker() as session:
            query = await session.execute(
                select(Query)
                .filter(cast(ColumnElement[bool], Query.user_id == user_id))
                .order_by(Query.created_at.desc())  # type: ignore
                .limit(1)
            )
            return query.scalar_one_or_none()
