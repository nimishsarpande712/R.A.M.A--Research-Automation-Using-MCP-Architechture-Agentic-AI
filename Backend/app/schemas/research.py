"""Research-specific schemas for RAMA project."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ResearchQuery(BaseModel):
    prompt: str
    include_workspace: bool = True
    include_mindmap: bool = True
    include_audio: bool = True
    include_summaries: bool = True
    include_citations: bool = True
    include_sample_paper: bool = True


class ResearchPaper(BaseModel):
    id: int
    title: str
    authors: List[str]
    abstract: str
    year: int
    journal: str
    citations: int
    relevance_score: int
    keywords: List[str]
    url: Optional[str] = None
    doi: Optional[str] = None


class WorkspaceTool(BaseModel):
    name: str
    status: str
    progress: int


class WorkspaceFile(BaseModel):
    name: str
    type: str
    size: str


class ResearchWorkspace(BaseModel):
    id: str
    name: str
    created_at: str
    tools: List[WorkspaceTool]
    files: List[WorkspaceFile]
    collaborators: int
    last_activity: str


# Enhanced Mindmap Schemas
class MindmapNode(BaseModel):
    id: int
    label: str
    x: float
    y: float
    type: str  # 'central', 'main', 'sub', 'author', 'concept', 'connection'
    size: Optional[int] = 20
    color: Optional[str] = "#4A90E2"
    description: Optional[str] = None
    references: Optional[List[str]] = []
    connections_count: Optional[int] = 0


class MindmapConnection(BaseModel):
    from_id: int = Field(alias="from")
    to_id: int = Field(alias="to")
    strength: Optional[float] = 1.0  # Connection strength 0-1
    type: Optional[str] = "related"  # 'related', 'authored', 'cites', 'extends'
    label: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class InteractiveMindmap(BaseModel):
    id: str
    topic: str
    nodes: List[MindmapNode]
    connections: List[MindmapConnection]
    metadata: Optional[Dict[str, Any]] = {}
    interactive_features: Optional[Dict[str, bool]] = {
        "zoom": True,
        "pan": True,
        "click_expand": True,
        "search": True,
        "filter": True
    }


# Comprehensive Summary Schemas
class TopicSummary(BaseModel):
    topic: str
    overview: str
    key_concepts: List[str]
    main_challenges: List[str]
    current_trends: List[str]
    future_directions: List[str]
    related_fields: List[str]


class DocumentSummary(BaseModel):
    paper_id: int
    title: str
    summary: str
    key_findings: List[str]
    methodology: str
    limitations: List[str]
    significance: str


class ComprehensiveSummaries(BaseModel):
    topic_overview: TopicSummary
    document_summaries: List[DocumentSummary]
    synthesis: str
    research_gaps: List[str]


# IEEE Citation Schemas
class IEEECitation(BaseModel):
    id: int
    paper_id: int
    citation_text: str
    citation_number: int
    in_text_format: str


class BibliographyEntry(BaseModel):
    id: int
    paper_id: int
    ieee_format: str
    bibtex_format: str
    apa_format: str
    mla_format: str


class AutomatedCitations(BaseModel):
    ieee_citations: List[IEEECitation]
    bibliography: List[BibliographyEntry]
    citation_count: int
    formatted_bibliography: str


# Sample Research Paper Schema
class ResearchPaperSection(BaseModel):
    title: str
    content: str
    subsections: Optional[List['ResearchPaperSection']] = []


class SampleResearchPaper(BaseModel):
    title: str
    abstract: str
    keywords: List[str]
    introduction: ResearchPaperSection
    literature_review: ResearchPaperSection
    methodology: ResearchPaperSection
    results: Optional[ResearchPaperSection] = None
    discussion: Optional[ResearchPaperSection] = None
    conclusion: ResearchPaperSection
    references: List[str]
    word_count: int
    generated_at: str


# Enhanced Research Response
class EnhancedResearchResponse(BaseModel):
    papers: List[ResearchPaper]
    workspace: Optional[ResearchWorkspace] = None
    interactive_mindmap: Optional[InteractiveMindmap] = None
    comprehensive_summaries: Optional[ComprehensiveSummaries] = None
    automated_citations: Optional[AutomatedCitations] = None
    sample_paper: Optional[SampleResearchPaper] = None
    audio_url: Optional[str] = None


# For backward compatibility
ResearchMindmap = InteractiveMindmap
ResearchResponse = EnhancedResearchResponse

# Enable forward references
ResearchPaperSection.model_rebuild()
