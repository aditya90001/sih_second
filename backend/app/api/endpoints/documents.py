from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.storage import StorageManager
from app.models.domain import Document, DocumentChunk
from app.models.enums import DataSourceType
from app.schemas.document import DocumentUploadResponse
from app.extraction.pdf_ingestor import PDFIngestor
from app.rag.engine import rag_engine

router = APIRouter()
storage_manager = StorageManager()
pdf_ingestor = PDFIngestor()

ALLOWED_EXTENSIONS = {"pdf", "csv"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB Limit

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    well_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    extension = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type .{extension}. Allowed types: PDF, CSV"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed limit of 25MB."
        )

    # 1. Save raw file with SHA256
    file_record = storage_manager.save_raw_file(
        file_content=content,
        file_name=file.filename,
        file_type=extension,
        source_name="USER_UPLOAD"
    )

    # 2. Check if document exists in DB
    existing_doc = db.query(Document).filter(Document.sha256 == file_record["sha256"]).first()
    if existing_doc:
        return DocumentUploadResponse(
            document_id=existing_doc.id,
            file_name=existing_doc.file_name,
            sha256=existing_doc.sha256,
            processing_status=existing_doc.processing_status,
            data_source_type=existing_doc.data_source_type,
            message="Document already exists and processed in system."
        )

    # 3. Save Document in DB
    doc_entry = Document(
        well_id=well_id,
        document_type=extension.upper(),
        file_name=file.filename,
        source_url=None,
        local_path=file_record["local_path"],
        sha256=file_record["sha256"],
        processing_status="PROCESSING",
        data_source_type=DataSourceType.USER_UPLOADED
    )
    db.add(doc_entry)
    db.commit()
    db.refresh(doc_entry)

    # 4. Extract Text & Chunking for RAG
    if extension == "pdf":
        pages = pdf_ingestor.extract_text_page_aware(file_record["local_path"])
        full_text = "\n".join([p["text"] for p in pages])
        doc_entry.extracted_text = full_text

        chunks_data = []
        chunk_idx = 0
        for p in pages:
            text = p["text"]
            if not text.strip():
                continue
            # Simple page-based chunking
            doc_chunk = DocumentChunk(
                document_id=doc_entry.id,
                chunk_index=chunk_idx,
                text=text,
                page_number=p["page"],
                metadata_json={"well_id": well_id, "page": p["page"]}
            )
            db.add(doc_chunk)
            chunks_data.append({
                "document_id": doc_entry.id,
                "chunk_index": chunk_idx,
                "text": text,
                "metadata": {
                    "document_id": doc_entry.id,
                    "well_id": well_id,
                    "page_number": p["page"],
                    "file_name": file.filename
                }
            })
            chunk_idx += 1

        db.commit()
        # Index in Vector Engine
        rag_engine.add_documents(chunks_data)

    doc_entry.processing_status = "COMPLETED"
    db.commit()

    return DocumentUploadResponse(
        document_id=doc_entry.id,
        file_name=doc_entry.file_name,
        sha256=doc_entry.sha256,
        processing_status=doc_entry.processing_status,
        data_source_type=doc_entry.data_source_type,
        message="Document uploaded, extracted, and indexed in RAG system successfully."
    )