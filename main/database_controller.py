import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


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
        self.engine = create_engine(f"mysql+mysqldb://{self.USERNAME}:{self.PASSWORD}@{self.ENDPOINT}:{self.PORT}/{self.DATABASE}")
        # Create a session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def close_connection(self):
        self.session.close()

    def append_df(self, df, table_name):
        df.to_sql(table_name, con=self.engine, if_exists='append', index=False)
        self.session.commit()


if __name__ == '__main__':
    poker_db = PokerDB()
    df = pd.DataFrame({
        'name': ['John', 'Jane', 'Doe'],
        'age': [28, 22, 25],
        'salary': [1000, 1500, 1300]
    })

    poker_db.build_connection()
    poker_db.append_df(df=df, table_name='test')
    poker_db.close_connection()


