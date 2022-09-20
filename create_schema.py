import pathlib
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import bindparam

from settings import settings
from models.tables import metadata_obj, evks_players


def create_schema(engine):
    metadata_obj.create_all(engine)


def insert_evks_players(engine):
    BASE_DIR = pathlib.Path(__file__).parent
    file_path = BASE_DIR / 'data' / 'evks_players.csv'

    with open(file_path, 'r') as file:
        lines = file.read().split('\n')

    columns = (
        'id',
        'first_name',
        'last_name',
        'itsf_first_name',
        'itsf_last_name',
        'itsf_license',
        'foreigner',
        'last_competition_date',
    )

    data = [dict(zip(columns, line.split(','))) for line in lines[1:-1]]
    for row in data:
        for key, value in row.items():
            if value is None or value == '' or value.upper() == 'NULL':
                row[key] = None

        row['foreigner'] = row['foreigner'] == '1'

        if dt := row['last_competition_date']:
            row['last_competition_date'] = datetime.strptime(dt, '%Y-%m-%d').date()

        if row['itsf_license'] == '0':
            row['itsf_license'] = None

    statement = evks_players.insert().values({column: bindparam(column) for column in columns})

    with sessionmaker(engine)() as session:
        session.execute(statement, data)
        session.commit()


if __name__ == "__main__":
    engine = create_engine(
        'postgresql://{user}:{password}@{host}:{port}/{database}'.format(**settings['db']),
        echo=True,
    )

    create_schema(engine)
    print('Created schema')

    insert_evks_players(engine)
    print('Inserted evks players')
