from sitaBot import DB_URI
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


def start() -> scoped_session:
    engine = create_engine(DB_URI, client_encoding="utf8")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    # Lightweight migrations for bigint Telegram IDs
    with engine.connect() as conn:
        for stmt in [
            'ALTER TABLE IF EXISTS users ALTER COLUMN user_id TYPE BIGINT USING user_id::bigint',
            'ALTER TABLE IF EXISTS approval ALTER COLUMN user_id TYPE BIGINT USING user_id::bigint',
            'ALTER TABLE IF EXISTS afk_users ALTER COLUMN user_id TYPE BIGINT USING user_id::bigint',
            'ALTER TABLE IF EXISTS warns ALTER COLUMN user_id TYPE BIGINT USING user_id::bigint',
            'ALTER TABLE IF EXISTS userinfo ALTER COLUMN user_id TYPE BIGINT USING user_id::bigint',
            'ALTER TABLE IF EXISTS userbio ALTER COLUMN user_id TYPE BIGINT USING user_id::bigint',
            'ALTER TABLE IF EXISTS gbans ALTER COLUMN user_id TYPE BIGINT USING user_id::bigint',
            'ALTER TABLE IF EXISTS connection ALTER COLUMN user_id TYPE BIGINT USING user_id::bigint',
            'ALTER TABLE IF EXISTS connection_history ALTER COLUMN user_id TYPE BIGINT USING user_id::bigint',
            'ALTER TABLE IF EXISTS chat_members ALTER COLUMN "user" TYPE BIGINT USING "user"::bigint',
        ]:
            try:
                conn.execute(text(stmt))
            except Exception:
                pass
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
SESSION = start()
