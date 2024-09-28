from typing import Any
from uuid import UUID

import sqlalchemy as sa
from alembic import op


def batch_update(
    table_name: str,
    id_column_name: str,
    ids: list[UUID],
    update_column_name: str,
    values: list[Any],
) -> None:
    if len(ids) != len(values):
        raise ValueError(
            f"ids and values must have the same length, but got {len(ids)} and {len(values)}"
        )
    if len(ids) == 0:
        return
    # Construct the CASE statement for the batch update
    cases = [f"WHEN :id_{i} THEN :value_{i}" for i in range(len(ids))]
    case_statement = f"CASE {id_column_name} {' '.join(cases)} END"
    # Construct and execute the batch update statement as a text query
    stmt = (
        f'UPDATE "{table_name}" SET {update_column_name} = {case_statement} WHERE {id_column_name} IN'  # noqa: S608
        f' ({",".join([":id_" + str(i) for i in range(len(ids))])})'
    )
    params = {f"id_{i}": id_val for i, id_val in enumerate(ids)}
    params.update({f"value_{i}": value for i, value in enumerate(values)})
    op.execute(sa.text(stmt).bindparams(**params))
