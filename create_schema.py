from sqlalchemy import create_engine
from settings import settings
from models import Base


def create_schema(engine):
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    engine = create_engine(
        'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
            **settings['db']
        ),
        echo=True,
    )
    create_schema(engine)
    print("Created schema")
