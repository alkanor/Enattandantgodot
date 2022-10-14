from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, ForeignKey, delete
from sqlalchemy.orm import relationship, reconstructor

from persistent.base import Base, BaseAndMetaChangeClassName, baseclass_for_sqlalchemy_with_subclass
from persistent.type_system import register_type
from persistent.base_type.string import String

from .alias import ALIAS
from .list import LIST

from enum import Enum


@register_type("ENUM", lambda enum_name, enum_values, session: (enum_name,))
def ENUM(enum_name, enum_values, session):
    STRING_LIST = LIST(String)
    enum_alias = ALIAS(STRING_LIST, f"ENUM<{enum_name}>", session)

    db_enum = enum_alias.GET_CREATE(session, name=enum_name)

    if not db_enum.entries:
        strings = [String.GET_CREATE(session, val) for val in enum_values]
        db_enum.add_many(session, strings)
    else:
        s1 = set(list_entry.entry.id for list_entry in db_enum.entries)
        s2 = set(enum_values)
        assert s1 == s2, f"Unmatched set for DB enum {enum_name}: {s1} in DB and {s2} asked"

    return Enum(enum_name, {list_entry.entry.id: list_entry.entry for list_entry in db_enum.entries})


if __name__ == "__main__":
    from persistent_to_disk import create_session

    session = create_session()

    e = ENUM("TESTENUM", ["started", "ended", "middle"], session)
    for elem in e:
        print(elem.name, type(elem.value))
