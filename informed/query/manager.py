from informed.db_models.query import Query
from uuid import UUID
from informed.db import session_maker
from sqlalchemy.sql import select, ColumnElement
from typing import cast
from informed.api.schema import UpdateQueryRequest, QueryResponse
from informed.db_models.query import QueryState
from asyncio import Event
from datetime import datetime, timedelta
import asyncio


class QueryManager:
    def __init__(self) -> None:
        self._query_updates: dict[UUID, Event] = {}
        self._last_updates: dict[UUID, datetime] = {}
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

        # Signal that a query has been updated
        if query.query_id in self._query_updates:
            self._last_updates[query.query_id] = datetime.now()
            self._query_updates[query.query_id].set()

    async def get_query(self, query_id: UUID) -> Query:
        async with session_maker() as session:
            query = await session.execute(
                select(Query)
                .filter(cast(ColumnElement[bool], Query.query_id == query_id))
                .with_for_update()
            )
            result = query.scalar_one_or_none()
            if result is None:
                raise ValueError(f"Query {query_id} not found")
            return result

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

    async def get_updated_query(
        self, query_id: UUID, timeout: float | None = None
    ) -> Query:
        # Create event if it doesn't exist
        if query_id not in self._query_updates:
            self._query_updates[query_id] = Event()
            self._last_updates[query_id] = datetime.now()

        # Wait for the update event
        try:
            await asyncio.wait_for(
                self._query_updates[query_id].wait(), timeout=timeout
            )
            self._query_updates[query_id].clear()
            return await self.get_query(query_id)
        except asyncio.TimeoutError:
            return await self.get_query(query_id)
        finally:
            # Cleanup if no updates for a while
            if datetime.now() - self._last_updates[query_id] > timedelta(minutes=30):
                self._query_updates.pop(query_id, None)
                self._last_updates.pop(query_id, None)
