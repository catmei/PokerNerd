import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, distinct, Column, Integer, String, JSON, FLOAT, and_

load_dotenv()

Base = declarative_base()


# Define the table structure as a class
class History_Detail(Base):
    __tablename__ = 'history_detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String(45))
    round = Column(String(45))
    player = Column(String(45))
    position = Column(String(45))
    action = Column(String(45))
    number = Column(Integer)
    pot_before = Column(Integer)
    pot_after = Column(Integer)
    stack_before = Column(Integer)
    stack_after = Column(Integer)
    my_cards = Column(JSON)
    table_cards = Column(JSON)
    equity = Column(FLOAT)


class History_Overview(Base):
    __tablename__ = 'history_overview'

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String(45))
    position = Column(String(45))
    hole_cards = Column(JSON)
    community_cards = Column(JSON)
    pnl = Column(Integer)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(45), nullable=False, unique=True)
    password = Column(String(45), nullable=False)


class UserGameMapping(Base):
    __tablename__ = 'user_game_mapping'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(45), nullable=False)
    game_id = Column(String(45), nullable=False)


class PokerDB:
    def __init__(self):
        # Replace these values with your RDS instance details
        self.ENDPOINT = os.getenv('RDS_DB_ENDPOINT')
        self.PORT = os.getenv('RDS_DB_PORT')
        self.USERNAME = os.getenv('RDS_DB_USER')
        self.PASSWORD = os.getenv('RDS_DB_PASSWORD')
        self.DATABASE = os.getenv('RDS_DB_NAME')

        # Create an engine
        self.engine = create_engine(
            f"mysql+pymysql://{self.USERNAME}:{self.PASSWORD}@{self.ENDPOINT}:{self.PORT}/{self.DATABASE}")
        # Create a session class with the engine
        self.Session = sessionmaker(bind=self.engine)

    def append_df(self, df, table_name):
        with self.Session() as session:
            df.to_sql(table_name, con=self.engine, if_exists='append', index=False)
            session.commit()

    def fetch_game_id(self):
        with self.Session() as session:
            distinct_game_ids = session.query(distinct(History_Detail.game_id)).all()
            game_ids = [item[0] for item in distinct_game_ids]
            return game_ids

    def fetch_history_by_game_id(self, user, game_id):
        with self.Session() as session:
            subquery = session.query(UserGameMapping.game_id).filter(UserGameMapping.username == user).subquery()

            history_detail = session.query(History_Detail).filter(
                History_Detail.game_id.in_(subquery),
                History_Detail.game_id == game_id
            )
            df_history_detail = pd.read_sql(history_detail.statement, session.bind)
            return df_history_detail

    def fetch_history_detail_by_timestamp(self, start, end):
        with self.Session() as session:
            history_detail = session.query(History_Detail).filter(History_Detail.game_id >= int(start / 1000),
                                                                       History_Detail.game_id <= int(end / 1000))
            df_history_detail = pd.read_sql(history_detail.statement, session.bind)
            return df_history_detail

    def fetch_history_overview_by_timestamp(self, user, start, end):
        with self.Session() as session:
            subquery = session.query(UserGameMapping.game_id).filter(UserGameMapping.username == user).subquery()

            history_overview = session.query(History_Overview).filter(
                and_(
                    History_Overview.game_id >= int(start / 1000),
                    History_Overview.game_id <= (int(end / 1000) + 86400),
                    History_Overview.game_id.in_(subquery)
                )
            )
            df_history_overview = pd.read_sql(history_overview.statement, session.bind)

            return df_history_overview

    def fetch_history_overview_by_id(self, user, game_id):
        with self.Session() as session:
            subquery = session.query(UserGameMapping.game_id).filter(UserGameMapping.username == user).subquery()

            history_overview = session.query(History_Overview).filter(
                    History_Overview.game_id.in_(subquery),
                    History_Overview.game_id == game_id
            )
            df_history_overview = pd.read_sql(history_overview.statement, session.bind)

            return df_history_overview

    def save_user_info(self, username, password):
        with self.Session() as session:
            user_exists = session.query(User).filter_by(username=username).first() is not None
            if user_exists:
                print(f"username {username} already exists")
                return False
            else:
                new_user = User(username=username, password=password)
                session.add(new_user)
                session.commit()
                print('save user info successfully')
                return True

    def fetch_user_info(self):
        with self.Session() as session:
            user_info = session.query(User)
            df_user_info = pd.read_sql(user_info.statement, session.bind)

            return df_user_info

    def verify_login(self, username, password):
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(username=username).one()

                if user.password == password:
                    print("Verified")
                    return True
                else:
                    print("Wrong Password")
                    return False

            except NoResultFound:
                print('Not Registered')
                return False

    def save_user_game_mapping(self, username, game_id):
        with self.Session() as session:
            new_mapping = UserGameMapping(username=username, game_id=game_id)
            session.add(new_mapping)
            session.commit()
            return True

