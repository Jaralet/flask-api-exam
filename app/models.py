from . import db
from datetime import datetime

class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Result(id={self.id}, name='{self.name}', score={self.score}, timestamp='{self.timestamp}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "timestamp": self.timestamp.isoformat()
        }