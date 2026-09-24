from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import DataSourceType, WellType, WellStatus, EventSeverity, EventType, UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ENGINEER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Well(Base):
    __tablename__ = "wells"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(String(50), unique=True, index=True, nullable=False)
    well_name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    field = Column(String(100), nullable=False)
    block = Column(String(100), nullable=False)
    operator = Column(String(100), nullable=False)
    spud_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    total_depth = Column(Float, nullable=False)
    current_depth = Column(Float, default=0.0)
    well_type = Column(Enum(WellType), default=WellType.HISTORICAL, nullable=False)
    status = Column(Enum(WellStatus), default=WellStatus.COMPLETED, nullable=False)
    data_source_type = Column(Enum(DataSourceType), default=DataSourceType.SYNTHETIC, nullable=False)
    source_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    formations = relationship("Formation", back_populates="well", cascade="all, delete-orphan")
    events = relationship("DrillingEvent", back_populates="well", cascade="all, delete-orphan")
    parameters = relationship("DrillingParameter", back_populates="well", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="well", foreign_keys="Document.well_id")

class Formation(Base):
    __tablename__ = "formations"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False)
    formation_name = Column(String(100), nullable=False)
    top_depth = Column(Float, nullable=False)
    bottom_depth = Column(Float, nullable=False)
    lithology = Column(String(100), nullable=False)
    pressure_regime = Column(String(100), nullable=False)
    risk_notes = Column(Text, nullable=True)
    data_source_type = Column(Enum(DataSourceType), default=DataSourceType.SYNTHETIC, nullable=False)

    well = relationship("Well", back_populates="formations")

class DrillingEvent(Base):
    __tablename__ = "drilling_events"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False)
    depth = Column(Float, nullable=False)
    formation = Column(String(100), nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    severity = Column(Enum(EventSeverity), nullable=False)
    description = Column(Text, nullable=False)
    cause = Column(Text, nullable=True)
    mitigation = Column(Text, nullable=True)
    npt_hours = Column(Float, default=0.0)
    event_date = Column(DateTime, nullable=True)
    source_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    page_number = Column(Integer, nullable=True)
    data_source_type = Column(Enum(DataSourceType), default=DataSourceType.SYNTHETIC, nullable=False)

    well = relationship("Well", back_populates="events")

class DrillingParameter(Base):
    __tablename__ = "drilling_parameters"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    depth = Column(Float, nullable=False)
    rop = Column(Float, nullable=False)
    wob = Column(Float, nullable=False)
    rpm = Column(Float, nullable=False)
    torque = Column(Float, nullable=False)
    hook_load = Column(Float, nullable=False)
    standpipe_pressure = Column(Float, nullable=False)
    mud_weight = Column(Float, nullable=False)
    flow_rate = Column(Float, nullable=False)
    pump_pressure = Column(Float, nullable=False)
    ecd = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    data_source_type = Column(Enum(DataSourceType), default=DataSourceType.SYNTHETIC, nullable=False)

    well = relationship("Well", back_populates="parameters")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id"), nullable=True)
    document_type = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    source_url = Column(String(512), nullable=True)
    local_path = Column(String(512), nullable=False)
    document_date = Column(DateTime, nullable=True)
    sha256 = Column(String(64), unique=True, nullable=False)
    extracted_text = Column(Text, nullable=True)
    processing_status = Column(String(50), default="PENDING")
    data_source_type = Column(Enum(DataSourceType), default=DataSourceType.USER_UPLOADED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    well = relationship("Well", back_populates="documents", foreign_keys=[well_id])

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    embedding_id = Column(String(100), nullable=True)

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False)
    depth = Column(Float, nullable=False)
    risk_type = Column(Enum(EventType), nullable=False)
    probability = Column(Float, nullable=False)
    model_version = Column(String(50), nullable=False)
    features_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False)
    depth = Column(Float, nullable=False)
    alert_type = Column(Enum(EventType), nullable=False)
    severity = Column(Enum(EventSeverity), nullable=False)
    message = Column(Text, nullable=False)
    historical_evidence_json = Column(JSON, nullable=False)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), nullable=False)
    source_url = Column(String(512), nullable=False)
    source_type = Column(String(50), nullable=False)
    access_method = Column(String(50), nullable=False)
    last_checked = Column(DateTime, nullable=True)
    status = Column(String(50), default="UNVERIFIED")
    description = Column(Text, nullable=True)