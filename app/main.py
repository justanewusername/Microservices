from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pika
import json



class BrokerManager:
    def __init__(queue_name: str, host: str):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        return channel

class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

        # Определение модели данных (ORM)
        class Link(self.Base):
            __tablename__ = "items"
            id = Column(Integer, primary_key=True)
            link = Column(String)
            status = Column(Integer, nullable=True)

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
        session.expunge_all()
        session.close()
        if link is None:
            return None
        return link.link
    
    def update_link(self, link_id: int, new_status: int):
        session = self.SessionLocal()
        link = session.query(self.Link).filter(self.Link.id == link_id).first()

        if link:
            link.status = new_status
            session.commit()
        else:
            return None
        session.expunge_all()
        session.close()
        return link



app = FastAPI()
db_manager = DatabaseManager("postgresql://user:qwerty@postgres:5432/mydbname")

queue_name = 'links'
channel = BrokerManager(queue_name, 'rabbitmq')


@app.post("/links/")
def create_link(link: str):
    res = db_manager.create_link(link)
    msg = json.dumps({'link_id': res.id, 'link': link})
    channel.basic_publish(exchange='', routing_key=queue_name, body=msg)
    return res

@app.get("/links/{link_id}")
def read_link(link_id: int):
    link_id = db_manager.read_link(link_id)
    if link_id is None:
            raise HTTPException(status_code=404, detail="Link not found")
    return link_id

@app.put("/links/{link_id}")
def update_link(link_id: int, status: int):
    updated_link = db_manager.update_link(link_id, status)
    if updated_link is None:
        raise HTTPException(status_code=404, detail="Link not found")