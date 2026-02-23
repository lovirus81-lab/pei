from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    diagrams = relationship("Diagram", back_populates="project")

class Diagram(Base):
    __tablename__ = "diagrams"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    diagram_type = Column(String, nullable=False) # 'PFD', 'PID', etc.
    version = Column(Integer, nullable=False, default=1)
    canonical_json = Column(JSON, nullable=False)
    canonical_schema_version = Column(Integer, nullable=False, default=1)
    status = Column(String, default='draft')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="diagrams")
    runs = relationship("Run", back_populates="diagram")

class Ruleset(Base):
    __tablename__ = "rulesets"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    hash = Column(String, nullable=False)
    status = Column(String, default='active')
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('name', 'version', name='uq_ruleset_name_version'),)

    rules = relationship("Rule", back_populates="ruleset")
    runs = relationship("Run", back_populates="ruleset")

class Rule(Base):
    __tablename__ = "rules"

    id = Column(String, primary_key=True, default=generate_uuid)
    ruleset_id = Column(String, ForeignKey("rulesets.id"), nullable=False)
    code = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=False)
    kind = Column(String, nullable=False) # 'lookup', 'validate', 'generate'
    scope = Column(String, nullable=False) # 'PFD', 'PID', 'both'
    severity = Column(String, nullable=True)
    name_ko = Column(String, nullable=False)
    name_en = Column(String, nullable=True)
    description = Column(String, nullable=True)
    condition_json = Column(JSON, nullable=True)
    action_json = Column(JSON, nullable=True)
    message_template = Column(String, nullable=True)
    reference = Column(String, nullable=True)
    layer = Column(String, nullable=False)
    priority = Column(Integer, default=100)
    is_overridable = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)

    ruleset = relationship("Ruleset", back_populates="rules")

class Run(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    diagram_id = Column(String, ForeignKey("diagrams.id"), nullable=False)
    diagram_version = Column(Integer, nullable=False)
    ruleset_id = Column(String, ForeignKey("rulesets.id"), nullable=False)
    ruleset_hash = Column(String, nullable=False)
    result_json = Column(JSON, nullable=False)
    passed = Column(Boolean, nullable=False)
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    diagram = relationship("Diagram", back_populates="runs")
    ruleset = relationship("Ruleset", back_populates="runs")
