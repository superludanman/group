from sqlalchemy import Column, Integer, String, UniqueConstraint
from .config import Base

class UserKnowledge(Base):
    __tablename__ = "user_knowledge"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), index=True)
    knowledge_id = Column(String(64), index=True)
    __table_args__ = (UniqueConstraint('user_id', 'knowledge_id', name='_user_knowledge_uc'),) 