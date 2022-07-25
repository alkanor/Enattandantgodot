from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
import sqlalchemy.types


class utcnow(expression.FunctionElement):
    type = sqlalchemy.types.DateTime()


@compiles(utcnow)
def utcnow__default(element, compiler, **kw):
    # sqlite uses UTC by default
    return "CURRENT_TIMESTAMP"

@compiles(utcnow, "postgresql")
def utcnow__postgresql(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
