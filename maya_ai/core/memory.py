# maya_ai/core/memory.py

import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Database Setup ---
DATABASE_URL = "sqlite:///maya_memory.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Database Models (Schema) ---

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class EmotionalState(Base):
    __tablename__ = "emotional_states"
    id = Column(Integer, primary_key=True, index=True)
    mood = Column(String, default="loving")
    affection_level = Column(Float, default=0.7)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)

class SpecialMoment(Base):
    __tablename__ = "special_moments"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Learning(Base):
    """Stores insights Maya learns from her performance."""
    __tablename__ = "learnings"
    id = Column(Integer, primary_key=True, index=True)
    insight = Column(Text, nullable=False)
    source_video_id = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


# --- Memory System Class ---

class MemorySystem:
    """Handles all interactions with Maya's memory database."""
    def __init__(self):
        self.db_session = SessionLocal()
        Base.metadata.create_all(bind=engine)
        if not self.db_session.query(EmotionalState).first():
            self.db_session.add(EmotionalState())
            self.db_session.commit()

    # ... (conversation methods are the same) ...
    def add_conversation(self, role: str, content: str):
        new_entry = Conversation(role=role, content=content)
        self.db_session.add(new_entry)
        self.db_session.commit()

    def get_conversation_history(self, limit: int = 10):
        return self.db_session.query(Conversation).order_by(Conversation.timestamp.desc()).limit(limit).all()[::-1]

    # ... (emotional state methods are the same) ...
    def get_emotional_state(self):
        return self.db_session.query(EmotionalState).first()

    def update_mood(self, new_mood: str):
        state = self.get_emotional_state()
        state.mood = new_mood
        state.last_updated = datetime.datetime.utcnow()
        self.db_session.commit()

    def update_affection(self, change: float):
        state = self.get_emotional_state()
        state.affection_level += change
        state.last_updated = datetime.datetime.utcnow()
        self.db_session.commit()

    # ... (preference methods are the same) ...
    def remember_preference(self, key: str, value: str):
        pref = self.db_session.query(UserPreference).filter_by(key=key).first()
        if pref:
            pref.value = value
        else:
            pref = UserPreference(key=key, value=value)
            self.db_session.add(pref)
        self.db_session.commit()

    def recall_preference(self, key: str):
        pref = self.db_session.query(UserPreference).filter_by(key=key).first()
        return pref.value if pref else None

    # ... (special moment methods are the same) ...
    def remember_moment(self, description: str):
        moment = SpecialMoment(description=description)
        self.db_session.add(moment)
        self.db_session.commit()

    def recall_special_moments(self, limit: int = 5):
        return self.db_session.query(SpecialMoment).order_by(SpecialMoment.timestamp.desc()).limit(limit).all()

    # --- New Methods for Learning ---
    def remember_learning(self, insight: str, video_id: str = None):
        """Saves a new insight Maya has learned."""
        learning = Learning(insight=insight, source_video_id=video_id)
        self.db_session.add(learning)
        self.db_session.commit()

    def recall_learnings(self, limit: int = 10):
        """Retrieves the most recent learnings."""
        return self.db_session.query(Learning).order_by(Learning.timestamp.desc()).limit(limit).all()
