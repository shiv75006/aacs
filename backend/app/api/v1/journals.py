"""Journal API endpoints"""
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Journal, JournalDetails
from app.schemas.journal import (
    JournalRequest, JournalResponse, JournalListResponse,
    JournalDetailRequest, JournalDetailResponse
)
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/api/v1/journals", tags=["Journals"])


@router.get(
    "/",
    response_model=List[JournalListResponse],
    status_code=status.HTTP_200_OK,
    summary="List all journals",
    description="Retrieve a list of all available journals with basic information"
)
async def list_journals(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of journals to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of journals to return")
):
    """
    Get all journals with pagination support.
    
    - **skip**: Number of journals to skip (default: 0)
    - **limit**: Maximum number of journals to return (default: 10, max: 100)
    """
    journals = db.query(Journal).offset(skip).limit(limit).all()
    return [
        JournalListResponse(
            id=j.fld_id,
            name=j.fld_journal_name,
            short_form=j.short_form,
            issn_online=j.issn_ol,
            issn_print=j.issn_prt,
            chief_editor=j.cheif_editor,
            journal_logo=j.journal_logo,
            description=j.description
        )
        for j in journals
    ]


@router.get(
    "/{journal_id}",
    response_model=JournalResponse,
    status_code=status.HTTP_200_OK,
    summary="Get journal details",
    description="Retrieve detailed information about a specific journal"
)
async def get_journal(journal_id: int, db: Session = Depends(get_db)):
    """
    Get a specific journal by ID with all details.
    
    - **journal_id**: The journal ID
    """
    journal = db.query(Journal).filter(Journal.fld_id == journal_id).first()
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal with ID {journal_id} not found"
        )
    return JournalResponse(
        id=journal.fld_id,
        name=journal.fld_journal_name,
        frequency=journal.freq,
        issn_online=journal.issn_ol,
        issn_print=journal.issn_prt,
        chief_editor=journal.cheif_editor,
        co_editor=journal.co_editor,
        abstract_indexing=journal.abs_ind,
        short_form=journal.short_form,
        journal_image=journal.journal_image,
        journal_logo=journal.journal_logo,
        guidelines=journal.guidelines,
        copyright=journal.copyright,
        membership=journal.membership,
        subscription=journal.subscription,
        publication=journal.publication,
        advertisement=journal.advertisement,
        description=journal.description,
        added_on=journal.added_on.isoformat() if journal.added_on else None
    )


@router.get(
    "/{journal_id}/details",
    response_model=JournalDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get journal extended details",
    description="Retrieve extended details (about, guidelines, scope, etc.) for a journal"
)
async def get_journal_details(journal_id: int, db: Session = Depends(get_db)):
    """
    Get extended details for a specific journal.
    
    - **journal_id**: The journal ID
    """
    # First check if journal exists
    journal = db.query(Journal).filter(Journal.fld_id == journal_id).first()
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal with ID {journal_id} not found"
        )
    
    # Get journal details
    journal_detail = db.query(JournalDetails).filter(
        JournalDetails.journal_id == str(journal_id)
    ).first()
    
    if not journal_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Details for journal {journal_id} not found"
        )
    
    return JournalDetailResponse(
        id=journal_detail.id,
        journal_id=journal_detail.journal_id,
        about_journal=journal_detail.about_journal,
        chief_say=journal_detail.cheif_say,
        aim_objective=journal_detail.aim_objective,
        criteria=journal_detail.criteria,
        scope=journal_detail.scope,
        guidelines=journal_detail.guidelines,
        readings=journal_detail.readings,
        added_on=journal_detail.added_on.isoformat() if journal_detail.added_on else None
    )


@router.post(
    "/",
    response_model=JournalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new journal",
    description="Create a new journal (admin only)"
)
async def create_journal(data: JournalRequest, db: Session = Depends(get_db)):
    """
    Create a new journal.
    
    Requires all mandatory fields. This is typically an admin operation.
    """
    # Check if journal with same name already exists
    existing = db.query(Journal).filter(
        Journal.fld_journal_name == data.fld_journal_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Journal '{data.fld_journal_name}' already exists"
        )
    
    # Create new journal
    new_journal = Journal(
        fld_journal_name=data.fld_journal_name,
        freq=data.freq,
        issn_ol=data.issn_ol,
        issn_prt=data.issn_prt,
        cheif_editor=data.cheif_editor,
        co_editor=data.co_editor,
        password=data.password,
        abs_ind=data.abs_ind,
        short_form=data.short_form,
        journal_image=data.journal_image,
        journal_logo=data.journal_logo,
        guidelines=data.guidelines,
        copyright=data.copyright,
        membership=data.membership,
        subscription=data.subscription,
        publication=data.publication,
        advertisement=data.advertisement,
        description=data.description,
        added_on=date.today()
    )
    
    db.add(new_journal)
    db.commit()
    db.refresh(new_journal)
    
    return JournalResponse(
        id=new_journal.fld_id,
        name=new_journal.fld_journal_name,
        frequency=new_journal.freq,
        issn_online=new_journal.issn_ol,
        issn_print=new_journal.issn_prt,
        chief_editor=new_journal.cheif_editor,
        co_editor=new_journal.co_editor,
        abstract_indexing=new_journal.abs_ind,
        short_form=new_journal.short_form,
        journal_image=new_journal.journal_image,
        journal_logo=new_journal.journal_logo,
        guidelines=new_journal.guidelines,
        copyright=new_journal.copyright,
        membership=new_journal.membership,
        subscription=new_journal.subscription,
        publication=new_journal.publication,
        advertisement=new_journal.advertisement,
        description=new_journal.description,
        added_on=new_journal.added_on.isoformat() if new_journal.added_on else None
    )


@router.put(
    "/{journal_id}",
    response_model=JournalResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a journal",
    description="Update journal information (admin only)"
)
async def update_journal(
    journal_id: int,
    data: JournalRequest,
    db: Session = Depends(get_db)
):
    """
    Update an existing journal.
    
    - **journal_id**: The journal ID to update
    """
    journal = db.query(Journal).filter(Journal.fld_id == journal_id).first()
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal with ID {journal_id} not found"
        )
    
    # Update fields - only update if provided, otherwise keep existing values
    journal.fld_journal_name = data.fld_journal_name
    journal.freq = data.freq if data.freq is not None else journal.freq
    journal.issn_ol = data.issn_ol if data.issn_ol is not None else journal.issn_ol
    journal.issn_prt = data.issn_prt if data.issn_prt is not None else journal.issn_prt
    journal.cheif_editor = data.cheif_editor if data.cheif_editor is not None else journal.cheif_editor
    journal.co_editor = data.co_editor if data.co_editor is not None else journal.co_editor
    journal.password = data.password
    journal.abs_ind = data.abs_ind if data.abs_ind is not None else journal.abs_ind
    journal.short_form = data.short_form
    journal.journal_image = data.journal_image if data.journal_image is not None else journal.journal_image
    journal.journal_logo = data.journal_logo if data.journal_logo is not None else journal.journal_logo
    journal.guidelines = data.guidelines if data.guidelines is not None else journal.guidelines
    journal.copyright = data.copyright if data.copyright is not None else journal.copyright
    journal.membership = data.membership if data.membership is not None else journal.membership
    journal.subscription = data.subscription if data.subscription is not None else journal.subscription
    journal.publication = data.publication if data.publication is not None else journal.publication
    journal.advertisement = data.advertisement if data.advertisement is not None else journal.advertisement
    journal.description = data.description if data.description is not None else journal.description
    
    db.commit()
    db.refresh(journal)
    
    return JournalResponse(
        id=journal.fld_id,
        name=journal.fld_journal_name,
        frequency=journal.freq,
        issn_online=journal.issn_ol,
        issn_print=journal.issn_prt,
        chief_editor=journal.cheif_editor,
        co_editor=journal.co_editor,
        abstract_indexing=journal.abs_ind,
        short_form=journal.short_form,
        journal_image=journal.journal_image,
        journal_logo=journal.journal_logo,
        guidelines=journal.guidelines,
        copyright=journal.copyright,
        membership=journal.membership,
        subscription=journal.subscription,
        publication=journal.publication,
        advertisement=journal.advertisement,
        description=journal.description,
        added_on=journal.added_on.isoformat() if journal.added_on else None
    )


@router.delete(
    "/{journal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a journal",
    description="Delete a journal (admin only)"
)
async def delete_journal(journal_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific journal.
    
    - **journal_id**: The journal ID to delete
    """
    journal = db.query(Journal).filter(Journal.fld_id == journal_id).first()
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal with ID {journal_id} not found"
        )
    
    # Also delete associated journal details
    db.query(JournalDetails).filter(JournalDetails.journal_id == str(journal_id)).delete()
    
    db.delete(journal)
    db.commit()
    
    return None
