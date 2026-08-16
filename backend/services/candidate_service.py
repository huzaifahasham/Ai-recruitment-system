import os
import uuid
import logging
from sqlalchemy.orm import Session
from fastapi import UploadFile

from backend.config import settings
from backend.utils.security import sanitize_filename, secure_filepath_join, validate_uploaded_file
from backend.database.repositories import CandidateRepository
from backend.cv_parser.pdf_parser import parse_pdf
from backend.cv_parser.docx_parser import parse_docx
from backend.cv_parser.txt_parser import parse_txt
from backend.cv_parser.text_cleaner import clean_cv_text

from backend.ai.cv_extractor import extract_cv_information
from backend.ai.domain_classifier import classify_candidate_domain
from backend.ai.screening_evaluator import evaluate_candidate_screening

logger = logging.getLogger(__name__)

class CandidateService:
    @staticmethod
    def save_and_initiate_cv(db: Session, file: UploadFile) -> str:
        """
        Saves uploaded file safely and initializes a candidate record in database.
        Returns the unique candidate_id.
        """
        filename = file.filename or "uploaded_cv.txt"
        sanitized = sanitize_filename(filename)
        
        # Read content bytes for size validation
        contents = file.file.read()
        file_size = len(contents)
        
        validate_uploaded_file(file, file_size)
        
        candidate_id = f"CAND-{uuid.uuid4().hex[:8].upper()}"
        file_ext = sanitized.split('.')[-1].lower() if '.' in sanitized else "txt"
        saved_filename = f"{candidate_id}_{sanitized}"
        
        save_path = secure_filepath_join(settings.UPLOAD_DIR, saved_filename)
        
        with open(save_path, "wb") as f:
            f.write(contents)
            
        logger.info(f"CV uploaded successfully: {saved_filename} (Size: {file_size} bytes)")

        # Create initial DB record
        CandidateRepository.create_candidate(db, {
            "id": candidate_id,
            "cv_filename": sanitized,
            "cv_path": save_path,
            "file_type": file_ext.upper(),
            "file_size_bytes": file_size,
            "status": "UPLOADED"
        })
        
        return candidate_id

    @staticmethod
    def process_candidate_cv(db: Session, candidate_id: str):
        """
        Executes end-to-end processing pipeline for a candidate:
        Parsing -> Cleaning -> Structured Extraction -> Domain Classification -> Screening Evaluation -> DB Save
        """
        logger.info(f"Starting pipeline processing for candidate {candidate_id}")
        CandidateRepository.update_status(db, candidate_id, "PROCESSING")
        
        candidate = CandidateRepository.get_by_id(db, candidate_id)
        if not candidate:
            logger.error(f"Candidate {candidate_id} not found in DB")
            return
            
        file_path = candidate.cv_path
        file_ext = candidate.file_type.lower()
        
        try:
            # Step 1: Parsing
            logger.info(f"Parsing CV text for {candidate_id} ({file_ext})")
            if file_ext == "pdf":
                raw_text = parse_pdf(file_path)
            elif file_ext == "docx":
                raw_text = parse_docx(file_path)
            elif file_ext == "txt":
                raw_text = parse_txt(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
            candidate.raw_text = raw_text
            db.commit()

            # Step 2: Cleaning & Normalization
            cleaned_text = clean_cv_text(raw_text)

            # Step 3: Candidate Information Extraction
            logger.info(f"Extracting candidate profile data via AI for {candidate_id}")
            extracted_info = extract_cv_information(cleaned_text)

            # Step 4: Domain Classification
            logger.info(f"Classifying candidate domain for {candidate_id}")
            domain_info = classify_candidate_domain(extracted_info, cleaned_text)

            # Step 5: Preliminary Screening Evaluation
            logger.info(f"Evaluating preliminary screening score for {candidate_id}")
            screening_info = evaluate_candidate_screening(extracted_info, domain_info)

            # Step 6: Save structured result in DB
            CandidateRepository.save_analysis_results(
                db=db,
                candidate_id=candidate_id,
                extracted_info=extracted_info,
                domain_info=domain_info,
                screening_info=screening_info
            )
            logger.info(f"Completed processing for candidate {candidate_id}. Primary Domain: {domain_info.get('primary_domain')}, Score: {screening_info.get('score')}")

        except Exception as e:
            logger.error(f"Failed to process candidate {candidate_id}: {str(e)}", exc_info=True)
            CandidateRepository.update_status(db, candidate_id, "FAILED", error_message=str(e))
