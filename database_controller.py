import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, distinct, Column, Integer, String, JSON, FLOAT
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

Base = declarative_base()


# Define the table structure as a class
class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String(45))
    round = Column(String(45))
    player = Column(String(45))
    position = Column(String(45))
    action = Column(String(45))
    number = Column(Integer)
    stack_before = Column(Integer)
    stack_after = Column(Integer)
    pot_before = Column(Integer)
    pot_after = Column(Integer)
    my_cards = Column(JSON)
    table_cards = Column(JSON)
    equity = Column(FLOAT)


class PokerDB:
    def __init__(self):
        # Replace these values with your RDS instance details
        self.ENDPOINT = os.getenv('RDS_DB_ENDPOINT')
        self.PORT = os.getenv('RDS_DB_PORT')
        self.USERNAME = os.getenv('RDS_DB_USER')
        self.PASSWORD = os.getenv('RDS_DB_PASSWORD')
        self.DATABASE = os.getenv('RDS_DB_NAME')

        self.session = None
        self.engine = None

    def build_connection(self):
        # Create an engine
        self.engine = create_engine(f"mysql+pymysql://{self.USERNAME}:{self.PASSWORD}@{self.ENDPOINT}:{self.PORT}/{self.DATABASE}")
        # Create a session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def close_connection(self):
        self.session.close()

    def append_df(self, df, table_name):
        df.to_sql(table_name, con=self.engine, if_exists='append', index=False)
        self.session.commit()

    def fetch_game_id(self):
        distinct_game_ids = self.session.query(distinct(History.game_id)).all()
        game_ids = [item[0] for item in distinct_game_ids]
        return game_ids

    def fetch_history_by_game_id(self, game_id):
        history = self.session.query(History).filter(History.game_id == game_id)
        # Convert the query results to a DataFrame
        df_history = pd.read_sql(history.statement, self.session.bind)
        return df_history


if __name__ == '__main__':
    poker_db = PokerDB()
    df = pd.DataFrame({
        'name': ['John', 'Jane', 'Doe'],
        'age': [28, 22, 25],
        'salary': [1000, 1500, 1300]
    })

    poker_db.build_connection()
    # poker_db.append_df(df=df, table_name='test')
    # poker_db.fetch_game_id()
    data = poker_db.fetch_history_by_game_id(game_id=1695736821)
    poker_db.close_connection()

    print(data)

