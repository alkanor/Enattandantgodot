from persistent.base_type import BasicEntity


def _META_SOMETHING(metaname, columns_dict, MetaAdditional=None):

    return BasicEntity(metaname, columns_dict, MetaAdditional, slug=metaname.split('<')[0])
