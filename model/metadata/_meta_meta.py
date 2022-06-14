from model.base_type import BasicEntity


def _META_SOMETHING(metaname, columns_dict, SQLAlchemyBaseType, MetaAdditional=None):

    return BasicEntity(f'{metaname}[{SQLAlchemyBaseType.__tablename__}]', columns_dict, MetaAdditional)
