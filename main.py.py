from datetime import datetime, time
import os
import threading
import time as time_module
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from Render environment variables, falling back to your provided URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://car_key_reg_db_user:d0ITR0KPgwm4Eeybq3yqe1oCgIEQY0SH@dpg-dar27rou01pc73e62i2g-a/car_key_reg_db",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DataRecord(Base):
  __tablename = "records"
  id = Column(Integer, primary_key=True, index=True)
  content = Column(Text, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI()

# Serve your frontend HTML file
app.mount("/", StaticFiles(directory=".", html=True), name="static")


class Item(BaseModel):
  content: str


class KeyPayload(BaseModel):
  registry: list
  nextNum: int


@app.post("/api/save")
def save_data(item: Item):
  db = SessionLocal()
  try:
    db_record = DataRecord(content=item.content)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return {"status": "success", "id": db_record.id}
  except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=str(e))
  finally:
    db.close()


@app.get("/api/keys")
def get_keys():
  db = SessionLocal()
  try:
    record = (
        db.query(DataRecord)
        .filter(DataRecord.content.like('%"registry"%'))
        .order_by(DataRecord.id.desc())
        .first()
    )
    if record:
      import json

      data = json.loads(record.content)
      return {"registry": data.get("registry", []), "nextNum": data.get("nextNum", 1)}
    return {"registry": [], "nextNum": 1}
  except Exception as e:
    return {"registry": [], "nextNum": 1}
  finally:
    db.close()


@app.post("/api/keys")
def save_keys(payload: KeyPayload):
  db = SessionLocal()
  try:
    import json

    content_str = json.dumps(
        {"registry": payload.registry, "nextNum": payload.nextNum}
    )
    db_record = DataRecord(content=content_str)
    db.add(db_record)
    db.commit()
    return {"status": "success"}
  except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=str(e))
  finally:
    db.close()


# --- Daily Backup Routine (4:00 PM to Render Portal storage) ---
def run_daily_backup_scheduler():
  os.makedirs("backups", exist_ok=True)
  last_backed_up_date = None

  while True:
    now = datetime.now()
    # Check if it is 4:00 PM (16:00)
    if (
        now.hour == 16
        and now.minute == 0
        and last_backed_up_date != now.date()
    ):
      db = SessionLocal()
      try:
        record = (
            db.query(DataRecord)
            .filter(DataRecord.content.like('%"registry"%'))
            .order_by(DataRecord.id.desc())
            .first()
        )
        if record:
          filename = f"backups/backup_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
          with open(filename, "w", encoding="utf-8") as f:
            f.write(record.content)
          print(f"Daily backup successfully saved to Render portal: {filename}")
          last_backed_up_date = now.date()
      except Exception as e:
        print(f"Error during scheduled daily backup: {e}")
      finally:
        db.close()
    time_module.sleep(30)  # Check every 30 seconds


# Start background backup worker thread
backup_thread = threading.Thread(target=run_daily_backup_scheduler, daemon=True)
backup_thread.start()