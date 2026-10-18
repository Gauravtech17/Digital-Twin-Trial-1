import os
from collections.abc import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
load_dotenv()
DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///./polypulse.db')
engine=create_engine(DATABASE_URL,future=True,pool_pre_ping=True,connect_args={'check_same_thread':False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False,expire_on_commit=False,class_=Session)
class Base(DeclarativeBase): pass
def get_db()->Generator[Session,None,None]:
 db=SessionLocal()
 try: yield db
 finally: db.close()
