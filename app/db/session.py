from sqlmodel import SQLModel, create_engine

DATABASE_URL = 'sqlite:///.autogram.db'

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={
        'check_same_thread': False
    },
)
