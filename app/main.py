from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

        # Определение модели данных (ORM) здесь
        class Link(self.Base):
            __tablename__ = "items"
            id = Column(Integer, primary_key=True, index=True)
            link = Column(String, index=True)

        self.Link = Link
        self.Base.metadata.create_all(bind=self.engine)

    def create_link(self, link: str):
        session = self.SessionLocal()
        new_link = self.Link(link=link)
        session.add(new_link)
        
        session.flush()
        session.refresh(new_link)

        session.expunge_all()
        session.commit()
        session.close()
        
        return {"id": new_link.id}

    def read_link(self, link_id: int):
        session = self.SessionLocal()
        link = session.query(self.Link).filter(self.Link.id == link_id).first()
        session.close()
        if link is None:
            return None
        return link.link


app = FastAPI()
db_manager = DatabaseManager("postgresql://user:qwerty@postgres:5432/mydbname")


@app.post("/links/")
def create_link(link: str):
    return db_manager.create_link(link)

@app.get("/links/{link_id}")
def read_link(link_id: int):
    link_id = db_manager.read_link(link_id)
    if link_id is None:
            raise HTTPException(status_code=404, detail="Link not found")
    return link_id
