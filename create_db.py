import logging
from db.session import engine
from db.base import Base
from db.models import *


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_table():
    logging.info("Creating tables in the database...")
    print("Creating tables in the database...")
    
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("All tables created successfully.")
        print("All tables created successfully.")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        print(f"Error creating tables: {e}")
    
if __name__ == "__main__":
    create_table()
