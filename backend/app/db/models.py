"""SQLAlchemy ORM Models mapped to MySQL database"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, func, Float
from datetime import datetime, date
from app.db.database import Base


class User(Base):
    """User model mapping to existing MySQL user table"""
    __tablename__ = "user"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=True, default="User")
    fname = Column(String(100), nullable=True)
    lname = Column(String(100), nullable=True)
    mname = Column(String(100), nullable=True)
    title = Column(String(100), nullable=True)
    affiliation = Column(String(255), nullable=True)
    specialization = Column(Text, nullable=True)
    contact = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    added_on = Column(DateTime, default=datetime.utcnow, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "fname": self.fname,
            "lname": self.lname,
            "mname": self.mname,
            "title": self.title,
            "affiliation": self.affiliation,
            "specialization": self.specialization,
            "contact": self.contact,
            "address": self.address,
            "added_on": self.added_on.isoformat() if self.added_on else None
        }

class Journal(Base):
    """Journal model mapping to existing MySQL journal table"""
    __tablename__ = "journal"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    fld_id = Column(Integer, primary_key=True, index=True)
    fld_journal_name = Column(String(200), nullable=True)
    freq = Column(String(250), nullable=True)  # Frequency
    issn_ol = Column(String(250), nullable=True)  # ISSN Online
    issn_prt = Column(String(250), nullable=True)  # ISSN Print
    cheif_editor = Column(String(250), nullable=True)
    co_editor = Column(String(250), nullable=True)
    password = Column(String(100), nullable=False)
    abs_ind = Column(String(300), nullable=True)  # Abstract Indexing
    short_form = Column(String(255), nullable=False)
    journal_image = Column(String(255), nullable=False)
    journal_logo = Column(String(200), nullable=False)
    guidelines = Column(String(200), nullable=False)
    copyright = Column(String(200), nullable=False)
    membership = Column(String(200), nullable=False)
    subscription = Column(String(200), nullable=False)
    publication = Column(String(200), nullable=False)
    advertisement = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    added_on = Column(Date, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.fld_id,
            "name": self.fld_journal_name,
            "frequency": self.freq,
            "issn_online": self.issn_ol,
            "issn_print": self.issn_prt,
            "chief_editor": self.cheif_editor,
            "co_editor": self.co_editor,
            "abstract_indexing": self.abs_ind,
            "short_form": self.short_form,
            "journal_image": self.journal_image,
            "journal_logo": self.journal_logo,
            "guidelines": self.guidelines,
            "copyright": self.copyright,
            "membership": self.membership,
            "subscription": self.subscription,
            "publication": self.publication,
            "advertisement": self.advertisement,
            "description": self.description,
            "added_on": self.added_on.isoformat() if self.added_on else None
        }


class JournalDetails(Base):
    """Journal Details model mapping to existing MySQL journal_details table"""
    __tablename__ = "journal_details"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(String(50), nullable=False)
    about_journal = Column(Text, nullable=True)
    cheif_say = Column(Text, nullable=True)  # Chief's say
    aim_objective = Column(Text, nullable=True)
    criteria = Column(Text, nullable=True)
    scope = Column(Text, nullable=True)
    guidelines = Column(Text, nullable=True)
    readings = Column(Text, nullable=True)
    added_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "journal_id": self.journal_id,
            "about_journal": self.about_journal,
            "chief_say": self.cheif_say,
            "aim_objective": self.aim_objective,
            "criteria": self.criteria,
            "scope": self.scope,
            "guidelines": self.guidelines,
            "readings": self.readings,
            "added_on": self.added_on.isoformat() if self.added_on else None
        }


class Paper(Base):
    """Paper/Submission model mapping to existing MySQL paper table"""
    __tablename__ = "paper"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    id = Column(Integer, primary_key=True, index=True)
    paper_code = Column(String(200), nullable=False, default="")
    journal = Column(String(12), nullable=False, default="")
    title = Column(String(500), nullable=False, default="")
    abstract = Column(String(1500), nullable=False, default="")
    keyword = Column(String(1000), nullable=False, default="")
    file = Column(String(200), nullable=False, default="")
    added_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    added_by = Column(String(100), nullable=False, default="")
    status = Column(String(50), nullable=False, default="submitted")
    mailstatus = Column(String(10), nullable=False, default="0")
    volume = Column(String(100), nullable=False, default="")
    issue = Column(String(100), nullable=False, default="")
    author = Column(String(100), nullable=False, default="")
    coauth = Column(String(200), nullable=False, default="")
    rev = Column(String(200), nullable=False, default="")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "paper_code": self.paper_code,
            "journal": self.journal,
            "title": self.title,
            "abstract": self.abstract,
            "keywords": self.keyword,
            "file": self.file,
            "added_on": self.added_on.isoformat() if self.added_on else None,
            "added_by": self.added_by,
            "status": self.status,
            "author": self.author,
            "coauth": self.coauth
        }


class PaperPublished(Base):
    """Published papers model"""
    __tablename__ = "paper_published"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False)
    abstract = Column(String(2000), nullable=False, default="")
    author = Column(String(1000), nullable=False, default="")
    journal = Column(String(250), nullable=False, default="")
    journal_id = Column(Integer, nullable=False)
    volume = Column(String(250), nullable=False, default="")
    issue = Column(String(250), nullable=False, default="")
    date = Column(DateTime, nullable=False)
    pages = Column(String(250), nullable=False, default="")
    keyword = Column(String(300), nullable=False, default="")
    language = Column(String(20), nullable=False, default="")
    paper = Column(String(200), nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "abstract": self.abstract,
            "author": self.author,
            "journal": self.journal,
            "journal_id": self.journal_id,
            "volume": self.volume,
            "issue": self.issue,
            "date": self.date.isoformat() if self.date else None,
            "pages": self.pages,
            "language": self.language
        }


class PaperComment(Base):
    """Paper comments/feedback model"""
    __tablename__ = "paper_comment"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, nullable=True)
    comment_by = Column(String(255), nullable=True)
    comment_text = Column(Text, nullable=True)
    added_on = Column(DateTime, nullable=True, default=datetime.utcnow)


class OnlineReview(Base):
    """Online review model"""
    __tablename__ = "online_review"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, nullable=True)
    reviewer_id = Column(String(100), nullable=True)
    assigned_on = Column(Date, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "paper_id": self.paper_id,
            "reviewer_id": self.reviewer_id,
            "assigned_on": self.assigned_on.isoformat() if self.assigned_on else None
        }


class Editor(Base):
    """Editor model"""
    __tablename__ = "editor"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    id = Column(Integer, primary_key=True, index=True)
    editor_name = Column(String(100), nullable=True)
    editor_email = Column(String(100), nullable=True)
    journal_id = Column(String(100), nullable=True)
    role = Column(String(50), nullable=True)


class ReviewerInvitation(Base):
    """Reviewer invitation model for tracking reviewer assignments and acceptances"""
    __tablename__ = "reviewer_invitation"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, nullable=False, index=True)
    reviewer_id = Column(Integer, nullable=True)  # Reviewer user ID (if known)
    reviewer_email = Column(String(255), nullable=False)
    reviewer_name = Column(String(255), nullable=True)
    journal_id = Column(String(100), nullable=True)
    
    # Invitation token for magic link
    invitation_token = Column(String(255), nullable=False, unique=True, index=True)
    token_expiry = Column(DateTime, nullable=False)
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, accepted, declined, expired
    
    # Timestamps
    invited_on = Column(DateTime, default=datetime.utcnow)
    accepted_on = Column(DateTime, nullable=True)
    declined_on = Column(DateTime, nullable=True)
    
    # Additional info
    invitation_message = Column(Text, nullable=True)
    decline_reason = Column(Text, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "paper_id": self.paper_id,
            "reviewer_id": self.reviewer_id,
            "reviewer_email": self.reviewer_email,
            "reviewer_name": self.reviewer_name,
            "journal_id": self.journal_id,
            "status": self.status,
            "invited_on": self.invited_on.isoformat() if self.invited_on else None,
            "accepted_on": self.accepted_on.isoformat() if self.accepted_on else None,
            "declined_on": self.declined_on.isoformat() if self.declined_on else None,
            "token_expiry": self.token_expiry.isoformat() if self.token_expiry else None,
        }