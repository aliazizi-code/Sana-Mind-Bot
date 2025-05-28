from db.session import engine
from db.base import Base
from models import *


def create_table():
    print("Creating tables in the database...")
    
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully.")
    
    
if __name__ == "__main__":
    create_table(   )
