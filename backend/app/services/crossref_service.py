"""
Crossref DOI Registration Service

This module handles DOI generation and registration with Crossref.
It follows the Crossref deposit XML schema 5.3.1 for journal articles.

DOI Pattern: {prefix}/{journal_short}.{year}.{volume}{issue}{paper_num}
Example: 10.58517/IJICM.2024.1101

Reference: https://www.crossref.org/documentation/schema-library/
"""
import httpx
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class DOIStatus(str, Enum):
    """DOI registration status"""
    PENDING = "pending"
    REGISTERED = "registered"
    FAILED = "failed"


class AccessType(str, Enum):
    """Paper access type"""
    SUBSCRIPTION = "subscription"
    OPEN = "open"


@dataclass
class CrossrefDepositResult:
    """Result of Crossref deposit operation"""
    success: bool
    batch_id: str
    doi: str
    message: str
    status: DOIStatus
    response_xml: Optional[str] = None


def generate_doi(
    journal_short: str,
    year: int,
    volume: str,
    issue: str,
    paper_num: int,
    prefix: str = None
) -> str:
    """
    Generate a DOI following Breakthrough Publishers pattern.
    
    Pattern: {prefix}/{journal_short}.{year}.{volume}{issue}{paper_num}
    
    Args:
        journal_short: Journal abbreviation (e.g., "IJICM", "ITMSC")
        year: Publication year
        volume: Volume number (will be zero-padded to 2 digits)
        issue: Issue number (will be zero-padded to 2 digits)
        paper_num: Paper number within the issue (will be zero-padded to 2 digits)
        prefix: DOI prefix (defaults to settings.CROSSREF_DOI_PREFIX)
    
    Returns:
        Complete DOI string (e.g., "10.58517/IJICM.2024.1101")
    
    Example:
        >>> generate_doi("IJICM", 2024, "11", "1", 1)
        "10.58517/IJICM.2024.1101"
    """
    if prefix is None:
        prefix = settings.CROSSREF_DOI_PREFIX
    
    # Normalize volume and issue to 2-digit strings
    vol_num = str(volume).zfill(2) if volume else "01"
    issue_num = str(issue).zfill(2) if issue else "01"
    paper_suffix = str(paper_num).zfill(2)
    
    # Generate DOI suffix
    suffix = f"{journal_short.upper()}.{year}.{vol_num}{issue_num}{paper_suffix}"
    
    return f"{prefix}/{suffix}"


class CrossrefService:
    """
    Service for interacting with Crossref DOI registration API.
    
    Handles XML generation and HTTP deposit to Crossref.
    """
    
    # Crossref XML namespaces
    CROSSREF_NS = "http://www.crossref.org/schema/5.3.1"
    XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
    SCHEMA_LOCATION = "http://www.crossref.org/schema/5.3.1 http://www.crossref.org/schemas/crossref5.3.1.xsd"
    
    def __init__(self):
        self.username = settings.CROSSREF_USERNAME
        self.password = settings.CROSSREF_PASSWORD
        self.prefix = settings.CROSSREF_DOI_PREFIX
        self.depositor_name = settings.CROSSREF_DEPOSITOR_NAME
        self.depositor_email = settings.CROSSREF_DEPOSITOR_EMAIL
        self.test_mode = settings.CROSSREF_TEST_MODE
        
        # Use test or production URL based on mode
        self.api_url = settings.CROSSREF_TEST_URL if self.test_mode else settings.CROSSREF_API_URL
    
    def build_crossref_xml(
        self,
        paper_data: Dict[str, Any],
        journal_data: Dict[str, Any],
        doi: str,
        batch_id: str = None
    ) -> str:
        """
        Build Crossref deposit XML for a journal article.
        
        Args:
            paper_data: Dictionary containing paper metadata:
                - title: Paper title
                - abstract: Paper abstract
                - authors: List of author dicts with name, affiliation, email
                - publication_date: Publication date
                - pages: Page range (e.g., "1-14")
                - url: Full-text URL (optional)
            journal_data: Dictionary containing journal metadata:
                - name: Full journal name
                - short_form: Journal abbreviation
                - issn_online: Online ISSN
                - issn_print: Print ISSN
                - volume: Volume number
                - issue: Issue number
            doi: The DOI to register
            batch_id: Unique batch identifier (auto-generated if not provided)
        
        Returns:
            XML string for Crossref deposit
        """
        if batch_id is None:
            batch_id = str(uuid.uuid4())
        
        # Create root element with namespaces
        root = ET.Element("doi_batch")
        root.set("version", "5.3.1")
        root.set("xmlns", self.CROSSREF_NS)
        root.set("xmlns:xsi", self.XSI_NS)
        root.set("xsi:schemaLocation", self.SCHEMA_LOCATION)
        
        # Head section
        head = ET.SubElement(root, "head")
        
        doi_batch_id = ET.SubElement(head, "doi_batch_id")
        doi_batch_id.text = batch_id
        
        timestamp = ET.SubElement(head, "timestamp")
        timestamp.text = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        
        depositor = ET.SubElement(head, "depositor")
        depositor_name_elem = ET.SubElement(depositor, "depositor_name")
        depositor_name_elem.text = self.depositor_name
        email_address = ET.SubElement(depositor, "email_address")
        email_address.text = self.depositor_email
        
        registrant = ET.SubElement(head, "registrant")
        registrant.text = self.depositor_name
        
        # Body section
        body = ET.SubElement(root, "body")
        
        # Journal metadata
        journal = ET.SubElement(body, "journal")
        
        journal_metadata = ET.SubElement(journal, "journal_metadata")
        journal_metadata.set("language", "en")
        
        full_title = ET.SubElement(journal_metadata, "full_title")
        full_title.text = journal_data.get("name", "")
        
        abbrev_title = ET.SubElement(journal_metadata, "abbrev_title")
        abbrev_title.text = journal_data.get("short_form", "")
        
        # ISSN
        if journal_data.get("issn_online"):
            issn_online = ET.SubElement(journal_metadata, "issn")
            issn_online.set("media_type", "electronic")
            issn_online.text = journal_data["issn_online"]
        
        if journal_data.get("issn_print"):
            issn_print = ET.SubElement(journal_metadata, "issn")
            issn_print.set("media_type", "print")
            issn_print.text = journal_data["issn_print"]
        
        # Journal issue
        journal_issue = ET.SubElement(journal, "journal_issue")
        
        pub_date = paper_data.get("publication_date", datetime.utcnow())
        if isinstance(pub_date, str):
            pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
        
        publication_date = ET.SubElement(journal_issue, "publication_date")
        publication_date.set("media_type", "online")
        
        month = ET.SubElement(publication_date, "month")
        month.text = str(pub_date.month).zfill(2)
        
        day = ET.SubElement(publication_date, "day")
        day.text = str(pub_date.day).zfill(2)
        
        year = ET.SubElement(publication_date, "year")
        year.text = str(pub_date.year)
        
        # Volume and issue
        if journal_data.get("volume"):
            journal_volume = ET.SubElement(journal_issue, "journal_volume")
            volume_elem = ET.SubElement(journal_volume, "volume")
            volume_elem.text = str(journal_data["volume"])
        
        if journal_data.get("issue"):
            issue_elem = ET.SubElement(journal_issue, "issue")
            issue_elem.text = str(journal_data["issue"])
        
        # Journal article
        journal_article = ET.SubElement(journal, "journal_article")
        journal_article.set("publication_type", "full_text")
        
        # Titles
        titles = ET.SubElement(journal_article, "titles")
        title = ET.SubElement(titles, "title")
        title.text = paper_data.get("title", "")
        
        # Contributors (authors)
        authors = paper_data.get("authors", [])
        if authors:
            contributors = ET.SubElement(journal_article, "contributors")
            
            for i, author in enumerate(authors):
                person_name = ET.SubElement(contributors, "person_name")
                person_name.set("sequence", "first" if i == 0 else "additional")
                person_name.set("contributor_role", "author")
                
                # Parse author name
                name_parts = author.get("name", "").strip().split()
                if name_parts:
                    given_name = ET.SubElement(person_name, "given_name")
                    given_name.text = " ".join(name_parts[:-1]) if len(name_parts) > 1 else name_parts[0]
                    
                    surname = ET.SubElement(person_name, "surname")
                    surname.text = name_parts[-1] if len(name_parts) > 1 else name_parts[0]
                
                # Affiliation
                if author.get("affiliation"):
                    affiliations = ET.SubElement(person_name, "affiliations")
                    institution = ET.SubElement(affiliations, "institution")
                    inst_name = ET.SubElement(institution, "institution_name")
                    inst_name.text = author["affiliation"]
        
        # Abstract
        if paper_data.get("abstract"):
            jats_abstract = ET.SubElement(journal_article, "jats:abstract")
            jats_abstract.set("xmlns:jats", "http://www.ncbi.nlm.nih.gov/JATS1")
            jats_p = ET.SubElement(jats_abstract, "jats:p")
            jats_p.text = paper_data["abstract"][:4000]  # Crossref limit
        
        # Publication date for article
        article_pub_date = ET.SubElement(journal_article, "publication_date")
        article_pub_date.set("media_type", "online")
        
        article_month = ET.SubElement(article_pub_date, "month")
        article_month.text = str(pub_date.month).zfill(2)
        
        article_day = ET.SubElement(article_pub_date, "day")
        article_day.text = str(pub_date.day).zfill(2)
        
        article_year = ET.SubElement(article_pub_date, "year")
        article_year.text = str(pub_date.year)
        
        # Pages
        if paper_data.get("pages"):
            pages = paper_data["pages"]
            pages_elem = ET.SubElement(journal_article, "pages")
            
            if "-" in pages:
                first_page, last_page = pages.split("-", 1)
                first_page_elem = ET.SubElement(pages_elem, "first_page")
                first_page_elem.text = first_page.strip()
                last_page_elem = ET.SubElement(pages_elem, "last_page")
                last_page_elem.text = last_page.strip()
            else:
                first_page_elem = ET.SubElement(pages_elem, "first_page")
                first_page_elem.text = pages.strip()
        
        # DOI data
        doi_data = ET.SubElement(journal_article, "doi_data")
        
        doi_elem = ET.SubElement(doi_data, "doi")
        doi_elem.text = doi
        
        resource = ET.SubElement(doi_data, "resource")
        # Generate the DOI resolution URL
        resource.text = paper_data.get("url", f"https://breakthroughpublishers.com/article/{doi}")
        
        # Convert to pretty-printed XML string
        xml_string = ET.tostring(root, encoding="unicode")
        
        # Add XML declaration
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        
        return xml_declaration + xml_string
    
    async def deposit_to_crossref(
        self,
        xml_data: str,
        batch_id: str
    ) -> CrossrefDepositResult:
        """
        Submit DOI deposit to Crossref API.
        
        Args:
            xml_data: Complete Crossref XML document
            batch_id: Unique batch identifier for tracking
        
        Returns:
            CrossrefDepositResult with success status and details
        """
        if not self.username or not self.password:
            logger.error("Crossref credentials not configured")
            return CrossrefDepositResult(
                success=False,
                batch_id=batch_id,
                doi="",
                message="Crossref credentials not configured. Set CROSSREF_USERNAME and CROSSREF_PASSWORD in environment.",
                status=DOIStatus.FAILED
            )
        
        # Prepare multipart form data
        files = {
            "fname": ("deposit.xml", xml_data, "application/xml")
        }
        
        data = {
            "operation": "doMDUpload",
            "login_id": self.username,
            "login_passwd": self.password
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    data=data,
                    files=files
                )
                
                response_text = response.text
                
                if response.status_code == 200:
                    # Check for success indicators in response
                    if "SUCCESS" in response_text.upper() or "QUEUED" in response_text.upper():
                        logger.info(f"DOI deposit successful for batch {batch_id}")
                        return CrossrefDepositResult(
                            success=True,
                            batch_id=batch_id,
                            doi="",  # Will be filled by caller
                            message="DOI deposit queued successfully with Crossref",
                            status=DOIStatus.REGISTERED,
                            response_xml=response_text
                        )
                    else:
                        logger.warning(f"DOI deposit returned unexpected response: {response_text[:500]}")
                        return CrossrefDepositResult(
                            success=True,  # HTTP was successful
                            batch_id=batch_id,
                            doi="",
                            message=f"Deposit submitted. Response: {response_text[:200]}",
                            status=DOIStatus.PENDING,
                            response_xml=response_text
                        )
                else:
                    logger.error(f"Crossref API error: {response.status_code} - {response_text[:500]}")
                    return CrossrefDepositResult(
                        success=False,
                        batch_id=batch_id,
                        doi="",
                        message=f"Crossref API error: {response.status_code} - {response_text[:200]}",
                        status=DOIStatus.FAILED,
                        response_xml=response_text
                    )
                    
        except httpx.TimeoutException:
            logger.error(f"Crossref API timeout for batch {batch_id}")
            return CrossrefDepositResult(
                success=False,
                batch_id=batch_id,
                doi="",
                message="Request to Crossref API timed out",
                status=DOIStatus.FAILED
            )
        except Exception as e:
            logger.error(f"Crossref deposit error: {str(e)}")
            return CrossrefDepositResult(
                success=False,
                batch_id=batch_id,
                doi="",
                message=f"Error communicating with Crossref: {str(e)}",
                status=DOIStatus.FAILED
            )
    
    async def register_doi(
        self,
        paper_data: Dict[str, Any],
        journal_data: Dict[str, Any],
        doi: str
    ) -> CrossrefDepositResult:
        """
        Complete DOI registration workflow.
        
        Generates XML and submits to Crossref.
        
        Args:
            paper_data: Paper metadata dictionary
            journal_data: Journal metadata dictionary
            doi: The DOI to register
        
        Returns:
            CrossrefDepositResult with registration status
        """
        batch_id = str(uuid.uuid4())
        
        # Build XML
        xml_data = self.build_crossref_xml(
            paper_data=paper_data,
            journal_data=journal_data,
            doi=doi,
            batch_id=batch_id
        )
        
        logger.info(f"Generated Crossref XML for DOI {doi}, batch {batch_id}")
        
        # Submit to Crossref
        result = await self.deposit_to_crossref(xml_data, batch_id)
        result.doi = doi
        
        return result
    
    async def check_deposit_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Check the status of a previous DOI deposit.
        
        Note: Crossref provides a separate status check API.
        
        Args:
            batch_id: The batch ID from the original deposit
        
        Returns:
            Dictionary with status information
        """
        status_url = f"https://doi.crossref.org/servlet/submissionDownload?usr={self.username}&pwd={self.password}&doi_batch_id={batch_id}&type=result"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(status_url)
                
                return {
                    "batch_id": batch_id,
                    "status_code": response.status_code,
                    "response": response.text[:1000] if response.text else None
                }
        except Exception as e:
            return {
                "batch_id": batch_id,
                "error": str(e)
            }


# Convenience function for direct use
async def register_paper_doi(
    paper_data: Dict[str, Any],
    journal_data: Dict[str, Any]
) -> CrossrefDepositResult:
    """
    Register a DOI for a paper.
    
    This is a convenience function that generates the DOI and registers it.
    
    Args:
        paper_data: Paper metadata including:
            - title, abstract, authors, publication_date, pages, url
            - paper_num: Paper number for DOI generation
        journal_data: Journal metadata including:
            - name, short_form, issn_online, issn_print, volume, issue
    
    Returns:
        CrossrefDepositResult with the registered DOI
    """
    service = CrossrefService()
    
    # Generate DOI
    pub_date = paper_data.get("publication_date", datetime.utcnow())
    if isinstance(pub_date, str):
        pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
    
    doi = generate_doi(
        journal_short=journal_data.get("short_form", "BP"),
        year=pub_date.year,
        volume=journal_data.get("volume", "1"),
        issue=journal_data.get("issue", "1"),
        paper_num=paper_data.get("paper_num", 1)
    )
    
    # Register with Crossref
    return await service.register_doi(paper_data, journal_data, doi)
