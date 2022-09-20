from sqlalchemy import create_engine
from settings import settings
from models.tables import metadata_obj


def create_schema(engine):
    metadata_obj.create_all(engine)


if __name__ == "__main__":
    engine = create_engine(
        'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
            **settings['db']
        ),
        echo=True,
    )
    create_schema(engine)
    print("Created schema")
