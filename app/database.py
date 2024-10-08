from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = "sqlite:///./coupons.db"

engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(bind=engine)

def close_db():
    engine.dispose()
