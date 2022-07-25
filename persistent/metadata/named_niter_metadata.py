from sqlalchemy import Column, Integer, String

from persistent.base_type import STRING_SIZE

from ._metadata_meta import _META_SOMETHING


def NAMED_NITER_METADATA(metadated_classname):

    tname_prefix = f'META_NAMED_NITER<{metadated_classname}>'

    columns = {
        "id": Column(Integer, primary_key=True),
        "name":  Column(String(STRING_SIZE)),
        "iter": Column(Integer, default=0),
    }

    return _META_SOMETHING(tname_prefix, columns)
