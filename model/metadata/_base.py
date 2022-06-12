from sqlalchemy.ext.declarative import declarative_base

from model._implem import BaseMetaType

from model.general import sql_bases


def BaseDictToAttrs(attr_dict):

    class MetaClassDictToAttrs(BaseMetaType):

        def __new__(cls, name, bases, dict):
            dict.update(attr_dict)
            return super().__new__(cls, name, bases, dict)

    BaseFromDict = declarative_base(metaclass = MetaClassDictToAttrs)
    sql_bases.append(BaseFromDict)

    return BaseFromDict