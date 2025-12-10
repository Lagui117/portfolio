"""Sport event model for storing match/game information."""
from datetime import datetime
from app.core.database import db


class SportEvent(db.Model):
    """Model for sports events (matches, games)."""
    
    __tablename__ = "sport_events"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # External API reference
    external_id = db.Column(db.String(100), unique=True, index=True)
    
    # Event details
    sport_type = db.Column(db.String(50), nullable=False, index=True)  # football, basketball, tennis, etc.
    league = db.Column(db.String(100), index=True)
    season = db.Column(db.String(20))
    
    # Teams/Competitors
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    
    # Match info
    event_date = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, live, finished, cancelled
    venue = db.Column(db.String(200))
    
    # Scores (null if not finished)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    
    # Odds
    odds_home = db.Column(db.Float)
    odds_draw = db.Column(db.Float)
    odds_away = db.Column(db.Float)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert event to dictionary."""
        return {
            'id': self.id,
            'external_id': self.external_id,
            'sport_type': self.sport_type,
            'league': self.league,
            'season': self.season,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'status': self.status,
            'venue': self.venue,
            'score': {
                'home': self.home_score,
                'away': self.away_score
            } if self.home_score is not None else None,
            'odds': {
                'home': self.odds_home,
                'draw': self.odds_draw,
                'away': self.odds_away
            } if self.odds_home else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<SportEvent {self.home_team} vs {self.away_team}>"


class TeamStatistics(db.Model):
    """Model for storing team statistics."""
    
    __tablename__ = "team_statistics"
    
    id = db.Column(db.Integer, primary_key=True)
    
    team_name = db.Column(db.String(100), nullable=False, index=True)
    sport_type = db.Column(db.String(50), nullable=False)
    season = db.Column(db.String(20), nullable=False)
    league = db.Column(db.String(100))
    
    # Statistics
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    
    # Goals/Points
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    
    # Form (last 5 matches: W/D/L)
    recent_form = db.Column(db.String(10))  # e.g., "WWDLW"
    
    # Computed
    win_rate = db.Column(db.Float)
    avg_goals_scored = db.Column(db.Float)
    avg_goals_conceded = db.Column(db.Float)
    
    # Timestamps
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_metrics(self):
        """Calculate derived metrics."""
        if self.matches_played > 0:
            self.win_rate = self.wins / self.matches_played
            self.avg_goals_scored = self.goals_for / self.matches_played
            self.avg_goals_conceded = self.goals_against / self.matches_played
        else:
            self.win_rate = 0.0
            self.avg_goals_scored = 0.0
            self.avg_goals_conceded = 0.0
    
    def to_dict(self):
        """Convert statistics to dictionary."""
        return {
            'id': self.id,
            'team_name': self.team_name,
            'sport_type': self.sport_type,
            'season': self.season,
            'league': self.league,
            'matches_played': self.matches_played,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'goals_for': self.goals_for,
            'goals_against': self.goals_against,
            'goal_difference': self.goals_for - self.goals_against,
            'win_rate': round(self.win_rate, 3) if self.win_rate else 0,
            'avg_goals_scored': round(self.avg_goals_scored, 2) if self.avg_goals_scored else 0,
            'avg_goals_conceded': round(self.avg_goals_conceded, 2) if self.avg_goals_conceded else 0,
            'recent_form': self.recent_form,
        }
    
    def __repr__(self):
        return f"<TeamStatistics {self.team_name} - {self.season}>"
