import os
from dotenv import load_dotenv
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy.engine.url import URL

load_dotenv()

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD", ""),
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "simple"),
    query={"charset": "utf8mb4"},
)

engine = create_engine(DATABASE_URL,pool_pre_ping=True,echo=False)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()

def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("""SELECT VERSION()"""))
        version = result.scalar()

        print("подключение к бд успешно")
        print(f"версия: {version}")
