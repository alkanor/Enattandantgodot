

if __name__ == "__main__":
    from persistent_to_disk import create_session
    from persistent.base_type import BasicEntity, STRING_SIZE

    from sqlalchemy import String, Integer, Column


    columns = {
        "id": Column(Integer, primary_key=True),
        "col1": Column(Integer),
        "col2": Column(Integer)
    }

    TOB = BasicEntity("testOrderby", columns)

    session = create_session()

    vals = [(1, 10), (1, 2), (2, 4), (5, 3), (1, 7), (4, 2), (1, 1), (3, 3), (6, 4), (3, 7)]

    for i,j in vals:
        v = TOB.GET_CREATE(session, col1=i, col2=j)

    print(session.query(TOB).order_by(TOB.col1, TOB.col2).all())
    print(session.query(TOB).order_by(TOB.col2, TOB.col1).all())

    print(session.query(TOB).order_by(TOB.col1, TOB.col2).group_by(TOB.col1).all())
    print(session.query(TOB).order_by(TOB.col2, TOB.col1).group_by(TOB.col2).all())

    print(session.query(TOB).group_by(TOB.col1).order_by(TOB.col1, TOB.col2).all())
    print(session.query(TOB).group_by(TOB.col2).order_by(TOB.col2, TOB.col1).all())

    from sqlalchemy import func

    subquery = session.query(
        TOB,
        func.rank().over(
            order_by=TOB.col2, #TOB.col2.desc()
            partition_by=TOB.col1
        ).label('rnk')
    ).subquery()

    query = session.query(subquery.c.col1, subquery.c.col2).filter(
        subquery.c.rnk == 1
    )
    print("\n".join(map(repr, query.all())))
