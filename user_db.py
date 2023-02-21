import sqlalchemy.exc as exc
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column('id', Integer, primary_key=True)

    def __init__(self, id):
        print(f'2{id}')
        self.id = id
               
    Uid = Column('Uid', String, default='None')
    Points = Column('Points', Integer, default=0)
    Wallet = Column('Wallet', String, default="None")



engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(bind=engine)
db = sessionmaker(bind=engine)()

def update():
    db.commit()

def get_user(user_id) -> User:
    user_id = int(user_id)
    try:
        return db.query(User).filter(User.id == user_id).one()
    except exc.NoResultFound as e:
        print(e, "Creating user table...")
        return create_user(user_id)

def create_user(user_id):
    try:
        user = User(user_id)

        db.add(user)

        update()

        return user
    except exc.IntegrityError as e: # Occurs when an object has the same key id as an object already in the table.
        print(e)
        return None

def remove_user(user_id):
    try:
        db.remove(db.query(User).filter(User.id == user_id).one())
        update()
        return True
    except exc.NoResultFound as e:
        print(e)
        return False

        