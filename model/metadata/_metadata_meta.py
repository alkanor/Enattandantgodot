from model.base_type import BasicEntity


def _META_SOMETHING(metaname, columns_dict, MetaAdditional=None):

    return BasicEntity(metaname, columns_dict, MetaAdditional, metaname.split('<')[0])
