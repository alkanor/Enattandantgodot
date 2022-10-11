from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy import and_, delete
from sqlalchemy.orm import relationship

from persistent.metadata.named_date_metadata import NAMED_DATE_METADATA
from persistent.base.baseclass_metadata import baseclass_for_metadata
from persistent.base import BaseAndMetaChangeClassName, BaseAndMetaFromAttrDict, sql_bases
from persistent.type_system import register_type

from itertools import product


__objectname__ = "MATRIX"


def colname(i):
    if i == 0:
        return "row"
    elif i == 1:
        return "col"
    else:
        return f"hypercol{i-2}"

def colnames(N):
    return list(map(colname, range(N)))

def repr_matrix_arg(matrix_arg):
    if type(matrix_arg) == int or type(matrix_arg) == str:
        return f'{matrix_arg}'
    else:
        return matrix_arg.__tablename__

def _MATRIX_DEPENDANCIES(SQLAlchemyValueType, *matrix_args, **additional_args_to_construct_metadata):
    MetadataType = additional_args_to_construct_metadata.get("metadata_type", None)
    if not MetadataType:
        MetadataClass = NAMED_DATE_METADATA(__objectname__)
    else:
        MetadataClass = MetadataType(__objectname__, *additional_args_to_construct_metadata.get('metadata_args', []))

    metaclass_tablename = MetadataClass.__tablename__
    entrytype_tablename = f'{__objectname__}<{MetadataClass.__slug__},{SQLAlchemyValueType.__tablename__},{",".join(map(repr_matrix_arg, matrix_args))}>'

    return metaclass_tablename, entrytype_tablename



def FakeClassForArg(index, matrix_arg):
    class sub:
        __tablename__ = f"{colname(index)}_{repr_matrix_arg(matrix_arg)}"
    return sub


@register_type(__objectname__, _MATRIX_DEPENDANCIES)
def MATRIX(SQLAlchemyValueType, *matrix_args, **additional_args_to_construct_metadata):
    metaclass_tablename, entrytype_tablename = _MATRIX_DEPENDANCIES(SQLAlchemyValueType, *matrix_args, **additional_args_to_construct_metadata)

    MetadataType = additional_args_to_construct_metadata.get("metadata_type", None)
    if not MetadataType:
        MetadataClass = NAMED_DATE_METADATA(__objectname__)
    else:
        MetadataClass = MetadataType(__objectname__, *additional_args_to_construct_metadata.get('metadata_args', []))

    assert (metaclass_tablename == MetadataClass.__tablename__)


    def relationship_col(i):
        def sub(cls):
            assert type(matrix_args[i]) != int and type(matrix_args[i]) != str, "Invalid type for relationship"
            return relationship(matrix_args[i], foreign_keys=[getattr(cls, f"{column_names[i]}_id")])
        return sub

    N = len(matrix_args)
    column_names = colnames(N)

    _, MetaBase = BaseAndMetaChangeClassName(SQLAlchemyValueType, MetadataClass,
                                             *[FakeClassForArg(*arg) for arg in enumerate(matrix_args)])

    #_, FinalMetaBase = BaseAndMetaFromAttrDict(columns, MetaBase)


    class AddDeclAttrMetaclass(MetaBase):

        def __new__(cls, name, bases, dict):
            for i, base_type in enumerate(matrix_args):
                if type(matrix_args[i]) == int:
                    dict.update({column_names[i]: Column(Integer)})
                elif type(matrix_args[i]) == str:
                    dict.update({column_names[i]: Column(String(256))})
                else:
                    dict.update({column_names[i]: declared_attr(relationship_col(i))})
                    dict.update({f"{column_names[i]}_id": Column(Integer, ForeignKey(base_type.id), nullable=False)})
            dict["__table_args__"] = (UniqueConstraint("metadata_id", *[f"{column_names[i]}_id" if type(matrix_args[i]) != int and type(matrix_args[i]) != str \
                                                                                                else column_names[i] \
                                                                        for i in range(N)], name='unique_row'),)
            return super().__new__(cls, name, bases, dict)

    BaseFromDict = declarative_base(metaclass=AddDeclAttrMetaclass)
    sql_bases.append(BaseFromDict)


    class _MATRIX_ENTRY(BaseFromDict):

        __tablename__ = entrytype_tablename
        __metadataclass__ = MetadataClass
        __basetype__ = SQLAlchemyValueType

        id = Column(Integer, primary_key=True)
        metadata_id = Column(Integer, ForeignKey(MetadataClass.id), nullable=False)
        value_id = Column(Integer, ForeignKey(SQLAlchemyValueType.id), nullable=True)

        @declared_attr
        def metadataobj(cls):
            return relationship(MetadataClass, foreign_keys=[cls.metadata_id])

        @declared_attr
        def value(cls):
            return relationship(SQLAlchemyValueType, foreign_keys=[cls.value_id])

        def location(self):
            base = [getattr(self, column_names[i]) for i in range(N)]
            return tuple(elem if type(elem) == int or type(elem) == str else elem.id for elem in base)

        def __repr__(self):
            return f'{self.metadataobj} - {", ".join([column_names[i]+":"+str(getattr(self, column_names[i])) for i in range(N)])} = {self.value}'


    class _MatrixGetItemHelper:
        def __init__(self, Ncols, matrixobj, args=None):
            self.Ncols = Ncols
            self.cur_args = args if args else []
            self.matrixobj = matrixobj

        def __getitem__(self, key):
            assert len(key) + len(self.cur_args) <= self.Ncols, "Too much items in key to get matrix value"
            new_args = list(self.cur_args)
            new_args.extend(key)
            if len(new_args) == self.Ncols:
                return self.resolve(new_args)
            else:
                return _MatrixGetItemHelper(self.Ncols, self.matrixobj, new_args)

        def __setitem__(self, key, value):
            if len(key) == self.Ncols:
                self.matrixobj[key] = value
            assert len(key) + len(self.cur_args) == self.Ncols, "Not enough items in key to set matrix value"
            new_args = list(self.cur_args)
            new_args.extend(key)
            self.matrixobj[new_args] = value

        def resolve(self, optional_args=None):
            if not optional_args:
                return self.matrixobj.get(self.cur_args)
            else:
                return self.matrixobj.get(optional_args)


    class _MATRIX(baseclass_for_metadata(MetadataClass)):

        __entrytype__ = _MATRIX_ENTRY
        __tablename__ = entrytype_tablename  # not a real SQLAlchemy table but to ease encapsulated type accesses
        __default_value__ = additional_args_to_construct_metadata.get("default", None)
        __autocommit__ = additional_args_to_construct_metadata.get("autocommit", False)

        def __init__(self, session, *args, **argv):
            if args:
                assert (type(args[0]) == self.__metadataclass__)
                self.metadata = args[0]
            else:
                self.metadata = MetadataClass.GET_CREATE(session, **argv)
            self.rows_initialized = False
            self._rows = []
            self._session_saved = session

        # lazy load matrix rows when needed, otherwise only the metadata suffices
        @property
        def rows(self):
            if not self.rows_initialized:
                self.rows_initialized = True
                self._rows = self._session_saved.query(_MATRIX_ENTRY).filter_by(metadata_id=self.metadata.id).all()
            return self._rows

        @rows.setter
        def rows(self, new_entries):
            self._rows = new_entries

        @rows.deleter
        def rows(self):
            self.rows_initialized = False
            self._rows = []

        def __getitem__(self, key):
            if type(key) == int or type(key) == str:
                key = [key]
            if len(key) == N:
                return self.get(key)
            else:
                return _MatrixGetItemHelper(N, self, key)

        @staticmethod
        def check_slice(k, i):
            assert k.start <= matrix_args[i], "Integers slice matrix index must be inferior to the matrix dimension"
            assert k.start >= 0, "Integers slice matrix index must be positive"
            assert k.stop <= matrix_args[i], "Integers slice matrix index must be inferior to the matrix dimension"
            assert k.stop >= 0, "Integers slice matrix index must be positive"
            assert k.start <= k.stop, "Start slice index must be inferior to stop slice"

        @staticmethod
        def derivate_key(key):
            to_set = []
            column_names_bis = ["" for _ in range(N)]
            for i, k in enumerate(key):
                column_names_bis[i] = column_names[i]
                if type(k) == slice:
                    _MATRIX.check_slice(k, i)
                    to_set.append(range(k.start, k.stop))
                else:
                    to_set.append([k])
            return product(*to_set), column_names_bis

        @staticmethod
        def to_int_tuple(tup):
            return tuple((x if type(x) == int or type(x) == str else x.id for x in tup))

        def construct_entry(self, value, location):
            return _MATRIX_ENTRY(metadataobj=self.metadata, value=value, **{colname: v for v, colname in location})

        def __setitem__(self, key, value, **argv):
            targets, location_names = _MATRIX.derivate_key(key)
            targets = list(targets)
            targets_to_int = list(map(_MATRIX.to_int_tuple, targets))
            entries = self.get(key)
            if type(entries) == _MATRIX_ENTRY: # shortcut if only one element set
                if len(targets) == 1: # we found the element
                    entries.value = value
                    if self.__autocommit__:
                        self._session_saved.commit()
                    return
                else: # we make a list of entries to keep compatibility
                    entries = [entries]

            for entry in entries:
                entry.value = value
                rel_location = entry.location()
                if rel_location in targets_to_int:
                    del targets[targets_to_int.index(rel_location)]
                    del targets_to_int[targets_to_int.index(rel_location)]

            for to_create in targets:
                session.add(self.construct_entry(value, zip(to_create, location_names)))
            if self.__autocommit__:
                self._session_saved.commit() # flag to commit or not (avoiding committing at every change)

        def get(self, key, session=None):
            if not session:
                session = self._session_saved
            else:
                self._session_saved = session
            assert len(key) <= N, "Key size must be inferior or equal to matrix size"
            queried = session.query(_MATRIX_ENTRY).filter_by(metadataobj=self.metadata)
            for i, k in enumerate(key):
                if type(k) == int:
                    assert k < matrix_args[i], "Integers matrix index must be inferior to the matrix dimension"
                    assert k >= 0, "Integers matrix index must be positive"
                if type(k) == slice:
                    self.check_slice(k, i)
                    queried = queried.filter(and_(getattr(_MATRIX_ENTRY, column_names[i]) >= k.start, getattr(_MATRIX_ENTRY, column_names[i]) < k.stop))
                else:
                    queried = queried.filter(getattr(_MATRIX_ENTRY, column_names[i]) == k)
            res = queried.all()
            if not res:
                from_key, location_names = _MATRIX.derivate_key(key)
                from_key = list(from_key)
                if len(from_key) == 1:
                    entry = self.construct_entry(self.__default_value__, zip(from_key[0], location_names))
                    session.add(entry)
                    return entry
                else:
                    entries = list(map(lambda k: self.construct_entry(self.__default_value__, zip(k, location_names)), from_key))
                    for entry in entries:
                        session.add(entry)
                    return entries
            elif len(res) == 1:
                return res[0]
            else:
                return res

        def clear(self, session=None):
            if not session:
                session = self._session_saved
            else:
                self._session_saved = session
            statement = delete(_MATRIX_ENTRY).where(_MATRIX_ENTRY.metadata_id == self.metadata.id)
            session.execute(statement)
            session.commit()
            MetadataClass.DELETE(session, id=self.metadata.id)
            self._rows = []
            self.rows_initialized = False

        def __repr__(self):
            return f'{self.metadata} : {self.rows}'

    return _MATRIX


if __name__ == "__main__":
    from persistent_to_disk import create_session
    from persistent.base_type import BasicEntity, STRING_SIZE

    from sqlalchemy.exc import IntegrityError, ArgumentError
    from sqlalchemy import String

    columns = {
        "id": Column(Integer, primary_key=True),
        "inmatrix": Column(String(STRING_SIZE), unique=True),
        "theforkey": Column(Integer, default=54326),
    }

    Test = BasicEntity("value", columns)

    columns_host = {
        "id": Column(Integer, primary_key=True),
        "host": Column(String(STRING_SIZE), unique=True),
        "ip": Column(Integer, default=54326),
    }

    Host = BasicEntity("HOST", columns_host)

    session = create_session()

    v1 = Test.GET_CREATE(session, inmatrix="bonjour1")
    v2 = Test.GET_CREATE(session, inmatrix="bonjour2")
    v3 = Test.GET_CREATE(session, inmatrix="bonjour3")
    v4 = Test.GET_CREATE(session, inmatrix="bonjour4")

    host = Host.GET_CREATE(session, host="pp", ip=87)

    MATRIX_TYPE = MATRIX(Test, 3, 5, Host, autocommit=True)
    print(MATRIX_TYPE)

    m1 = MATRIX_TYPE(session, name="xx")
    m1[0:2, 3:4, host] = v3
    print(m1[0, 3, host])

    try:
        m1[0, 5, host]
        raise Exception("Should not happen")
    except AssertionError:
        print("Normal assertion error index too high")

    try:
        print(m1[0:3, v1, "iij"])
        raise Exception("Should not happen")
    except ArgumentError:
        print("Normal argument error because v1")

    m1[0:3, 0:5, host] = v1

    print(m1[0].resolve())

    MATRIX_TYPE2 = MATRIX(Test, 3, 5, Host)
    print(MATRIX_TYPE == MATRIX_TYPE2)

    MATRIX_TYPE3 = MATRIX(Test, 4, 5, Host)
    print(MATRIX_TYPE3 == MATRIX_TYPE2)

    m2 = MATRIX_TYPE2(session, name="xx")
    print(m2)
    m2 = MATRIX_TYPE2.GET_CREATE(session, name="xx")
    print(m2)
    m3 = MATRIX_TYPE3(session, name="xx")
    print(m3)
