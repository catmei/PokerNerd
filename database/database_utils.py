import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, distinct, Column, Integer, String, JSON, FLOAT, and_, select
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm.exc import NoResultFound

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
        # Create a session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def append_df(self, df, table_name):
        df.to_sql(table_name, con=self.engine, if_exists='append', index=False)
        self.session.commit()

    def fetch_game_id(self):
        distinct_game_ids = self.session.query(distinct(History_Detail.game_id)).all()
        game_ids = [item[0] for item in distinct_game_ids]
        return game_ids

    def fetch_history_by_game_id(self, user, game_id):
        subquery = self.session.query(UserGameMapping.game_id).filter(UserGameMapping.username == user).subquery()

        history_detail = self.session.query(History_Detail).filter(
            History_Detail.game_id.in_(subquery),
            History_Detail.game_id == game_id
        )
        df_history_detail = pd.read_sql(history_detail.statement, self.session.bind)
        return df_history_detail

    def fetch_history_detail_by_timestamp(self, start, end):
        history_detail = self.session.query(History_Detail).filter(History_Detail.game_id >= int(start / 1000),
                                                                   History_Detail.game_id <= int(end / 1000))
        df_history_detail = pd.read_sql(history_detail.statement, self.session.bind)
        return df_history_detail

    def fetch_history_overview_by_timestamp(self, user, start, end):
        subquery = self.session.query(UserGameMapping.game_id).filter(UserGameMapping.username == user).subquery()

        history_overview = self.session.query(History_Overview).filter(
            and_(
                History_Overview.game_id >= int(start / 1000),
                History_Overview.game_id <= int(end / 1000),
                History_Overview.game_id.in_(subquery)
            )
        )
        df_history_overview = pd.read_sql(history_overview.statement, self.session.bind)

        return df_history_overview

    def fetch_history_overview_by_id(self, user, game_id):
        subquery = self.session.query(UserGameMapping.game_id).filter(UserGameMapping.username == user).subquery()

        history_overview = self.session.query(History_Overview).filter(
                History_Overview.game_id.in_(subquery),
                History_Overview.game_id == game_id
        )
        df_history_overview = pd.read_sql(history_overview.statement, self.session.bind)

        return df_history_overview

    def save_user_info(self, username, password):
        user_exists = self.session.query(User).filter_by(username=username).first() is not None
        if user_exists:
            print(f"username {username} already exists")
            return False
        else:
            new_user = User(username=username, password=password)
            self.session.add(new_user)
            self.session.commit()
            print('save user info successfully')
            return True

    def fetch_user_info(self):
        user_info = self.session.query(User)
        df_user_info = pd.read_sql(user_info.statement, self.session.bind)

        return df_user_info

    def verify_login(self, username, password):
        try:
            user = self.session.query(User).filter_by(username=username).one()

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
        new_mapping = UserGameMapping(username=username, game_id=game_id)
        self.session.add(new_mapping)
        self.session.commit()
        return True


if __name__ == '__main__':
    poker_db_dao = PokerDB()
    poker_db_dao.build_connection()

    # ids = poker_db_dao.fetch_game_id()
    # print(ids)

    # data = poker_db_dao.fetch_history_by_game_id(game_id=1695973800)
    # print(data)
    #
    # new_row = pd.DataFrame({
    #     'game_id': data['game_id'].tolist()[-1],
    #     'hole_cards': [data['my_cards'].tolist()[-1]],
    #     'community_cards': [data['table_cards'].tolist()[-1]],
    #     'pnl': 500
    # })
    # import json
    # new_row['hole_cards'] = new_row['hole_cards'].apply(json.dumps)
    # new_row['community_cards'] = new_row['community_cards'].apply(json.dumps)
    #
    # print(new_row)

    # poker_db_dao.append_df(df=new_row, table_name='history_overview')

    # get history by timestamp
    # start = 1695859200000
    # end = 1696118400000
    # poker_db_dao = PokerDB()
    # poker_db_dao.build_connection()
    # df_history = poker_db_dao.fetch_history_by_timestamp(start, end)
    # df_history = df_history[['']]
    # print(df_history.columns)

    poker_db_dao.save_user_info(username='new_username', password='new_password')
    # user_info = poker_db_dao.fetch_user_info()
    poker_db_dao.close_connection()
    #
    # print(df_history)
