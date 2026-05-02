import io
import structlog

logger = structlog.get_logger()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        full_text = "\n\n".join(text_parts)
        logger.info("pdf_parsed", pages=len(text_parts), text_length=len(full_text))
        return full_text
    except Exception as e:
        logger.error("pdf_parse_failed", error=str(e))
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n".join(paragraphs)
        logger.info("docx_parsed", paragraphs=len(paragraphs), text_length=len(full_text))
        return full_text
    except Exception as e:
        logger.error("docx_parse_failed", error=str(e))
        return ""


def extract_text(file_bytes: bytes, file_type: str) -> str:
    if file_type == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif file_type == "docx":
        return extract_text_from_docx(file_bytes)
    else:
        logger.error("unsupported_file_type", file_type=file_type)
        return ""