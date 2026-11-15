"""Create any missing tables, and migrate pre-existing tourism.db safely."""
import sqlite3
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
DATABASE_PATH=BASE_DIR/'database'/'tourism.db'
SCHEMA_PATH=BASE_DIR/'database'/'schema.sql'

def initialize_database():
    DATABASE_PATH.parent.mkdir(exist_ok=True,parents=True)
    with sqlite3.connect(DATABASE_PATH) as db:
        db.executescript(SCHEMA_PATH.read_text(encoding='utf-8'))
        for table in ('destinations','attractions','hotels'):
            existing={r[1] for r in db.execute('PRAGMA table_info('+table+')')}
            for col in ('latitude','longitude'):
                if col not in existing:
                    db.execute('ALTER TABLE '+table+' ADD COLUMN '+col+' REAL')
        hotel_fields={r[1] for r in db.execute('PRAGMA table_info(hotels)')}
        if 'booking_url' not in hotel_fields:
            db.execute('ALTER TABLE hotels ADD COLUMN booking_url TEXT')
        # Preserve destination IDs and their attraction / hotel relations when renaming.
        old=db.execute("SELECT id FROM destinations WHERE slug='george-town'").fetchone()
        current=db.execute("SELECT id FROM destinations WHERE slug='penang'").fetchone()
        if old and not current:
            db.execute("UPDATE destinations SET name=?,slug=?,description=? WHERE id=?",(
                'Penang','penang','Penang Island’s heritage, beaches and renowned food culture, including George Town.',old[0]))
        db.execute('CREATE INDEX IF NOT EXISTS idx_attractions_destination ON attractions(destination_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_hotels_destination ON hotels(destination_id)')
    print('Database schema ready; older data preserved.')

if __name__=='__main__':initialize_database()
