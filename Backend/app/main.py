from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
import asyncio
import json
import re

from .core import config
from .db.session import get_db
from .schemas.auth import UserLogin, Token, UserRegister, UserOut
from .schemas.research import (
    ResearchQuery, ResearchPaper, ResearchWorkspace, WorkspaceTool, WorkspaceFile,
    InteractiveMindmap, MindmapNode, MindmapConnection, EnhancedResearchResponse,
    ComprehensiveSummaries, TopicSummary, DocumentSummary, AutomatedCitations,
    IEEECitation, BibliographyEntry, SampleResearchPaper, ResearchPaperSection
)
from .db import models  # Assuming a models module exists
from .db.session import engine
from .mcp_client import mcp_client

logger = logging.getLogger(__name__)

app = FastAPI(title="R.A.M.A Backend", version="0.1.0")

# CORS settings - allow the React frontend (default CRA dev server)
origins = [config.FRONTEND_ORIGIN]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use bcrypt with manual length truncation to avoid issues
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def truncate_password(password: str, max_length: int = 72) -> str:
    """Truncate password to max_length bytes to avoid bcrypt limitations."""
    encoded = password.encode('utf-8')
    return encoded[:max_length].decode('utf-8', errors='ignore')


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.ALGORITHM)
    return encoded_jwt


def test_db_connection_via_engine():
    """Lightweight connectivity check using the configured SQLAlchemy engine.

    For Postgres, this verifies server reachability. For SQLite, it's a no-op sanity check.
    """
    try:
        with engine.connect() as conn:
            # Use driver-level SQL to avoid dialect-specific imports
            conn.exec_driver_sql("SELECT 1")
        return True
    except Exception as e:
        logger.warning("DB connectivity check failed: %s", e)
        return False

@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)
    # Only perform connectivity check explicitly for Postgres to avoid noisy logs when using SQLite fallback
    backend = engine.dialect.name
    if backend == "postgresql":
        ok = test_db_connection_via_engine()
        if ok:
            logger.info("PostgreSQL connectivity OK via SQLAlchemy engine.")
        else:
            logger.warning("PostgreSQL connectivity failed at startup. Check NETWORK/DNS/SSL settings.")
    else:
        logger.info("Using %s database backend (likely SQLite fallback for local dev).", backend)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "R.A.M.A FastAPI is running"}


@app.post("/api/auth/login", response_model=Token)
def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.email).first()
    # Truncate password before verification
    truncated_password = truncate_password(form_data.password)
    if not user or not pwd_context.verify(truncated_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/auth/register", response_model=UserOut, status_code=201)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Truncate password to avoid bcrypt limitations
    truncated_password = truncate_password(payload.password)
    hashed = pwd_context.hash(truncated_password)
    user = models.User(email=payload.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Mock data for research papers
MOCK_RESEARCH_PAPERS = [
    {
        "id": 1,
        "title": "Quantum Computing Applications in Neural Network Optimization",
        "authors": ["Dr. Sarah Chen", "Prof. Michael Rodriguez", "Dr. Aisha Patel"],
        "abstract": "This paper explores the revolutionary potential of quantum computing in optimizing neural network architectures. We present a novel quantum-classical hybrid approach that demonstrates 300% improvement in convergence rates for deep learning models.",
        "year": 2024,
        "journal": "Nature Quantum Information",
        "citations": 247,
        "relevance_score": 95,
        "keywords": ["quantum computing", "neural networks", "optimization", "hybrid algorithms"]
    },
    {
        "id": 2,
        "title": "Neuromorphic Computing: Bridging Biology and Silicon",
        "authors": ["Dr. Elena Vasquez", "Prof. James Liu", "Dr. Robert Thompson"],
        "abstract": "We investigate bio-inspired computing architectures that mimic neural structures. Our findings show significant energy efficiency improvements of up to 1000x compared to traditional von Neumann architectures.",
        "year": 2024,
        "journal": "IEEE Transactions on Neural Networks",
        "citations": 189,
        "relevance_score": 87,
        "keywords": ["neuromorphic", "bio-inspired", "energy efficiency", "brain-computer interface"]
    },
    {
        "id": 3,
        "title": "Large Language Models for Scientific Discovery",
        "authors": ["Dr. Alex Turner", "Prof. Maria Santos", "Dr. David Kim"],
        "abstract": "This comprehensive study examines how large language models can accelerate scientific research through automated hypothesis generation and literature synthesis. We demonstrate novel applications in drug discovery and materials science.",
        "year": 2024,
        "journal": "Science",
        "citations": 432,
        "relevance_score": 92,
        "keywords": ["language models", "scientific discovery", "automation", "hypothesis generation"]
    },
    {
        "id": 4,
        "title": "Edge AI: Bringing Intelligence to IoT Devices",
        "authors": ["Dr. Jennifer Wang", "Prof. Carlos Silva", "Dr. Ahmed Hassan"],
        "abstract": "We present novel architectures for deploying artificial intelligence on resource-constrained edge devices. Our approach achieves 95% accuracy while consuming 10x less power than traditional cloud-based solutions.",
        "year": 2024,
        "journal": "IEEE Internet of Things Journal",
        "citations": 156,
        "relevance_score": 78,
        "keywords": ["edge computing", "IoT", "artificial intelligence", "power efficiency"]
    },
    {
        "id": 5,
        "title": "Federated Learning for Privacy-Preserving AI",
        "authors": ["Dr. Rachel Green", "Prof. Antonio Lopez", "Dr. Yuki Tanaka"],
        "abstract": "This work addresses privacy concerns in machine learning by developing federated learning protocols that maintain data privacy while achieving comparable model performance to centralized approaches.",
        "year": 2024,
        "journal": "ACM Transactions on Privacy and Security",
        "citations": 234,
        "relevance_score": 85,
        "keywords": ["federated learning", "privacy", "distributed computing", "machine learning"]
    }
]


def generate_mock_workspace(topic: str) -> ResearchWorkspace:
    """Generate a mock research workspace based on the topic."""
    return ResearchWorkspace(
        id=f"ws_{int(datetime.now().timestamp())}",
        name=f"Research Workspace: {topic}",
        created_at=datetime.now().isoformat(),
        tools=[
            WorkspaceTool(name="Literature Review", status="active", progress=85),
            WorkspaceTool(name="Data Analysis", status="pending", progress=0),
            WorkspaceTool(name="Hypothesis Generator", status="active", progress=67),
            WorkspaceTool(name="Collaboration Hub", status="ready", progress=100)
        ],
        files=[
            WorkspaceFile(name="research_notes.md", type="markdown", size="2.3 KB"),
            WorkspaceFile(name="data_analysis.ipynb", type="jupyter", size="1.7 MB"),
            WorkspaceFile(name="references.bib", type="bibliography", size="45 KB")
        ],
        collaborators=3,
        last_activity="2 minutes ago"
    )


def generate_mock_mindmap(topic: str) -> InteractiveMindmap:
    """Generate a mock research mindmap based on the topic."""
    return InteractiveMindmap(
        id=f"mm_{int(datetime.now().timestamp())}",
        topic=topic,
        nodes=[
            MindmapNode(id=1, label=topic, x=300, y=200, type='central', size=30, color="#FF6B6B"),
            MindmapNode(id=2, label="Key Concepts", x=150, y=100, type='main', size=25, color="#4ECDC4"),
            MindmapNode(id=3, label="Applications", x=450, y=100, type='main', size=25, color="#45B7D1"),
            MindmapNode(id=4, label="Challenges", x=150, y=300, type='main', size=25, color="#96CEB4"),
            MindmapNode(id=5, label="Future Directions", x=450, y=300, type='main', size=25, color="#FFEAA7"),
            MindmapNode(id=6, label="Algorithms", x=100, y=50, type='sub', size=20, color="#DDA0DD"),
            MindmapNode(id=7, label="Optimization", x=200, y=50, type='sub', size=20, color="#98D8C8"),
            MindmapNode(id=8, label="Real-world Uses", x=400, y=50, type='sub', size=20, color="#F7DC6F"),
            MindmapNode(id=9, label="Industry Applications", x=500, y=50, type='sub', size=20, color="#BB8FCE"),
            # Author nodes
            MindmapNode(id=10, label="Dr. Sarah Chen", x=250, y=350, type='author', size=15, color="#82E0AA"),
            MindmapNode(id=11, label="Prof. Michael Rodriguez", x=350, y=350, type='author', size=15, color="#82E0AA"),
        ],
        connections=[
            MindmapConnection(from_id=1, to_id=2, strength=1.0, type="main_concept"),
            MindmapConnection(from_id=1, to_id=3, strength=1.0, type="main_concept"),
            MindmapConnection(from_id=1, to_id=4, strength=1.0, type="main_concept"),
            MindmapConnection(from_id=1, to_id=5, strength=1.0, type="main_concept"),
            MindmapConnection(from_id=2, to_id=6, strength=0.8, type="subconcept"),
            MindmapConnection(from_id=2, to_id=7, strength=0.8, type="subconcept"),
            MindmapConnection(from_id=3, to_id=8, strength=0.7, type="subconcept"),
            MindmapConnection(from_id=3, to_id=9, strength=0.7, type="subconcept"),
            MindmapConnection(from_id=10, to_id=1, strength=0.9, type="authored"),
            MindmapConnection(from_id=11, to_id=1, strength=0.9, type="authored"),
        ],
        metadata={
            "creation_date": datetime.now().isoformat(),
            "complexity_level": "intermediate",
            "node_count": 11,
            "connection_count": 10
        }
    )


def generate_comprehensive_summaries(topic: str, papers: List[ResearchPaper]) -> ComprehensiveSummaries:
    """Generate comprehensive summaries for research topic and papers."""
    # Topic overview
    topic_overview = TopicSummary(
        topic=topic,
        overview=f"This comprehensive analysis explores {topic} and its various applications, methodologies, and implications in modern research. The field has seen significant advancement in recent years with emerging trends and breakthrough technologies.",
        key_concepts=[
            "Machine Learning Algorithms",
            "Neural Network Architectures", 
            "Data Processing",
            "Optimization Techniques",
            "Real-world Applications"
        ],
        main_challenges=[
            "Scalability Issues",
            "Data Quality and Availability",
            "Computational Complexity",
            "Ethical Considerations",
            "Integration with Existing Systems"
        ],
        current_trends=[
            "AI-Driven Automation",
            "Edge Computing Integration",
            "Privacy-Preserving Technologies",
            "Cross-disciplinary Applications",
            "Open Source Development"
        ],
        future_directions=[
            "Quantum Computing Integration",
            "Sustainable Computing Solutions",
            "Enhanced Human-AI Collaboration",
            "Advanced Optimization Algorithms",
            "Interdisciplinary Research Expansion"
        ],
        related_fields=[
            "Computer Science",
            "Data Science",
            "Mathematics",
            "Engineering",
            "Cognitive Science"
        ]
    )
    
    # Document summaries
    document_summaries = []
    for i, paper in enumerate(papers[:5]):  # Limit to first 5 papers
        doc_summary = DocumentSummary(
            paper_id=paper.id,
            title=paper.title,
            summary=f"This research presents innovative approaches to {topic.lower()}, demonstrating significant improvements over existing methodologies. The study addresses key challenges in the field and provides valuable insights for future research directions.",
            key_findings=[
                f"Improved performance metrics by {85 + i*5}%",
                f"Novel {topic.lower()} algorithm development",
                "Comprehensive experimental validation",
                "Real-world application demonstration"
            ],
            methodology=f"The authors employed a mixed-methods approach combining theoretical analysis with empirical validation. Experiments were conducted using industry-standard datasets and benchmarking protocols.",
            limitations=[
                "Limited dataset size for some experiments",
                "Computational resource constraints",
                "Scope limited to specific application domains",
                "Need for long-term validation studies"
            ],
            significance=f"This work makes significant contributions to {topic.lower()} research by introducing novel algorithms and demonstrating their practical applicability across various domains."
        )
        document_summaries.append(doc_summary)
    
    return ComprehensiveSummaries(
        topic_overview=topic_overview,
        document_summaries=document_summaries,
        synthesis=f"The collected research on {topic} reveals a rapidly evolving field with significant potential for practical applications. Current work focuses on addressing scalability and efficiency challenges while exploring novel algorithmic approaches. The integration of emerging technologies presents both opportunities and challenges for future development.",
        research_gaps=[
            "Limited cross-domain validation studies",
            "Insufficient focus on long-term sustainability",
            "Need for standardized evaluation metrics",
            "Lack of comprehensive user studies",
            "Limited exploration of ethical implications"
        ]
    )


def generate_automated_citations(papers: List[ResearchPaper]) -> AutomatedCitations:
    """Generate automated IEEE citations and bibliography."""
    ieee_citations = []
    bibliography_entries = []
    
    for i, paper in enumerate(papers):
        citation_num = i + 1
        
        # IEEE Citation
        authors_str = paper.authors[0] if paper.authors else "Unknown Author"
        if len(paper.authors) > 1:
            authors_str += " et al."
            
        ieee_citation = IEEECitation(
            id=citation_num,
            paper_id=paper.id,
            citation_text=f'[{citation_num}] {authors_str}, "{paper.title}," {paper.journal}, vol. XX, no. X, pp. XX-XX, {paper.year}.',
            citation_number=citation_num,
            in_text_format=f"[{citation_num}]"
        )
        ieee_citations.append(ieee_citation)
        
        # Bibliography Entry
        authors_formatted = ", ".join(paper.authors[:3])  # Limit to first 3 authors
        if len(paper.authors) > 3:
            authors_formatted += " et al."
            
        ieee_format = f'[{citation_num}] {authors_formatted}, "{paper.title}," {paper.journal}, vol. XX, no. X, pp. XX-XX, {paper.year}.'
        
        # BibTeX format
        bibtex_key = f"{paper.authors[0].split()[-1].lower()}{paper.year}" if paper.authors else f"unknown{paper.year}"
        bibtex_format = f"""@article{{{bibtex_key},
    title={{{paper.title}}},
    author={{{" and ".join(paper.authors)}}},
    journal={{{paper.journal}}},
    year={{{paper.year}}},
    volume={{XX}},
    number={{X}},
    pages={{XX--XX}}
}}"""
        
        # APA format
        apa_format = f'{authors_formatted} ({paper.year}). {paper.title}. {paper.journal}, XX(X), XX-XX.'
        
        # MLA format
        mla_format = f'{authors_formatted}. "{paper.title}." {paper.journal}, vol. XX, no. X, {paper.year}, pp. XX-XX.'
        
        bib_entry = BibliographyEntry(
            id=citation_num,
            paper_id=paper.id,
            ieee_format=ieee_format,
            bibtex_format=bibtex_format,
            apa_format=apa_format,
            mla_format=mla_format
        )
        bibliography_entries.append(bib_entry)
    
    # Formatted bibliography string
    formatted_bibliography = "REFERENCES\n\n" + "\n\n".join([entry.ieee_format for entry in bibliography_entries])
    
    return AutomatedCitations(
        ieee_citations=ieee_citations,
        bibliography=bibliography_entries,
        citation_count=len(papers),
        formatted_bibliography=formatted_bibliography
    )


def generate_sample_research_paper(topic: str, papers: List[ResearchPaper]) -> SampleResearchPaper:
    """Generate a comprehensive sample research paper."""
    current_time = datetime.now().isoformat()
    
    # Introduction section
    introduction = ResearchPaperSection(
        title="Introduction",
        content=f"""The field of {topic} has emerged as one of the most significant areas of research in recent years, offering unprecedented opportunities for technological advancement and practical applications. This paper presents a comprehensive analysis of current research trends, methodologies, and future directions in {topic.lower()}.

The rapid evolution of this field has been driven by several key factors including technological advances, increased computational power, and the growing availability of large-scale datasets. Research in {topic.lower()} has demonstrated remarkable potential for addressing complex real-world problems across various domains.

This study aims to provide a systematic review of the current state-of-the-art in {topic.lower()}, identify key research gaps, and propose future research directions. We analyze {len(papers)} significant research papers to present a comprehensive overview of the field.""",
        subsections=[
            ResearchPaperSection(
                title="Background and Motivation", 
                content=f"The motivation for this research stems from the growing importance of {topic.lower()} in addressing contemporary challenges. Recent developments have shown significant promise in improving efficiency and effectiveness across multiple application domains."
            ),
            ResearchPaperSection(
                title="Research Objectives",
                content="The primary objectives of this research are: (1) to provide a comprehensive analysis of current research trends, (2) to identify key methodological approaches, (3) to highlight significant research gaps, and (4) to propose future research directions."
            )
        ]
    )
    
    # Literature Review section
    literature_review = ResearchPaperSection(
        title="Literature Review",
        content=f"""This section presents a comprehensive review of existing literature in {topic.lower()}. We systematically analyze recent research contributions and identify key trends and methodological approaches.

The literature review is organized into several key themes: foundational concepts, methodological innovations, application domains, and emerging trends. Each theme is discussed in detail with reference to relevant research contributions.""",
        subsections=[
            ResearchPaperSection(
                title="Foundational Concepts",
                content=f"The foundational concepts in {topic.lower()} provide the theoretical framework for understanding current research developments. Key concepts include algorithmic approaches, optimization techniques, and evaluation methodologies."
            ),
            ResearchPaperSection(
                title="Methodological Approaches",
                content="Recent research has introduced various methodological innovations including novel algorithms, optimization techniques, and evaluation frameworks. These approaches have demonstrated significant improvements over traditional methods."
            ),
            ResearchPaperSection(
                title="Application Domains",
                content=f"Research in {topic.lower()} has found applications across diverse domains including healthcare, finance, transportation, and environmental monitoring. Each application domain presents unique challenges and opportunities."
            )
        ]
    )
    
    # Methodology section
    methodology = ResearchPaperSection(
        title="Methodology",
        content=f"""This research employs a systematic literature review methodology to analyze current research in {topic.lower()}. We collected and analyzed {len(papers)} research papers from leading conferences and journals in the field.

The methodology consists of several key phases: paper selection and filtering, systematic analysis, trend identification, and gap analysis. Each phase is designed to ensure comprehensive coverage and objective analysis.""",
        subsections=[
            ResearchPaperSection(
                title="Data Collection",
                content="Papers were selected from major databases including IEEE Xplore, ACM Digital Library, and arXiv. Selection criteria included relevance, recency, and impact factor of the publication venue."
            ),
            ResearchPaperSection(
                title="Analysis Framework",
                content="We developed a comprehensive analysis framework focusing on methodological approaches, evaluation metrics, application domains, and reported performance improvements."
            )
        ]
    )
    
    # Conclusion section
    conclusion = ResearchPaperSection(
        title="Conclusion",
        content=f"""This paper has presented a comprehensive analysis of current research in {topic.lower()}. Our review of {len(papers)} research papers reveals significant progress in the field with several key trends and opportunities for future development.

Key findings include the emergence of novel algorithmic approaches, increasing focus on practical applications, and growing emphasis on evaluation standardization. However, several research gaps remain, including the need for long-term validation studies and cross-domain applicability analysis.

Future research directions should focus on addressing scalability challenges, developing standardized evaluation frameworks, and exploring interdisciplinary applications. The field shows tremendous potential for continued growth and practical impact."""
    )
    
    # Generate references
    references = []
    for i, paper in enumerate(papers):
        authors_str = ", ".join(paper.authors[:3])
        if len(paper.authors) > 3:
            authors_str += " et al."
        references.append(f'[{i+1}] {authors_str}, "{paper.title}," {paper.journal}, {paper.year}.')
    
    return SampleResearchPaper(
        title=f"A Comprehensive Analysis of Current Research Trends in {topic}",
        abstract=f"This paper presents a systematic review and analysis of current research trends in {topic.lower()}. Through comprehensive analysis of {len(papers)} research papers, we identify key methodological approaches, application domains, and future research directions. Our findings reveal significant progress in algorithmic development and practical applications, while highlighting important research gaps that require future attention. The analysis provides valuable insights for researchers and practitioners working in this rapidly evolving field.",
        keywords=[topic.lower(), "research analysis", "systematic review", "trends", "applications"],
        introduction=introduction,
        literature_review=literature_review,
        methodology=methodology,
        conclusion=conclusion,
        references=references,
        word_count=1250,  # Approximate word count
        generated_at=current_time
    )


async def research_query_fallback(query: ResearchQuery, db: Session):
    """Fallback function when MCP server is unavailable."""
    # Filter papers based on relevance to the prompt
    prompt_lower = query.prompt.lower()
    relevant_papers = []
    
    for paper in MOCK_RESEARCH_PAPERS:
        # Check if any keywords match the prompt
        relevance = 0
        for keyword in paper["keywords"]:
            if keyword.lower() in prompt_lower:
                relevance += 20
        
        # Check if prompt words appear in title or abstract
        prompt_words = prompt_lower.split()
        for word in prompt_words:
            if len(word) > 3:  # Only check significant words
                if word in paper["title"].lower():
                    relevance += 15
                if word in paper["abstract"].lower():
                    relevance += 10
        
        # Update relevance score based on matches
        if relevance > 0:
            paper_copy = paper.copy()
            paper_copy["relevance_score"] = min(paper["relevance_score"] + relevance, 100)
            relevant_papers.append(paper_copy)
    
    # If no specific matches found, return all papers with lower relevance
    if not relevant_papers:
        relevant_papers = [
            {**paper, "relevance_score": max(40, paper["relevance_score"] - 30)}
            for paper in MOCK_RESEARCH_PAPERS
        ]
    
    # Sort by relevance score
    relevant_papers.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Convert to Pydantic models
    papers = [ResearchPaper(**paper) for paper in relevant_papers]
    
    # Generate workspace if requested
    workspace = generate_mock_workspace(query.prompt) if query.include_workspace else None
    
    # Generate mindmap if requested
    mindmap = generate_mock_mindmap(query.prompt) if query.include_mindmap else None
    
    # Generate comprehensive summaries if requested
    summaries = generate_comprehensive_summaries(query.prompt, papers) if query.include_summaries else None
    
    # Generate automated citations if requested
    citations = generate_automated_citations(papers) if query.include_citations else None
    
    # Generate sample research paper if requested
    sample_paper = generate_sample_research_paper(query.prompt, papers) if query.include_sample_paper else None
    
    # Generate mock audio URL if requested
    audio_url = "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA..." if query.include_audio else None
    
    return EnhancedResearchResponse(
        papers=papers,
        workspace=workspace,
        interactive_mindmap=mindmap,
        comprehensive_summaries=summaries,
        automated_citations=citations,
        sample_paper=sample_paper,
        audio_url=audio_url
    )


@app.post("/api/research/query", response_model=EnhancedResearchResponse)
async def research_query(query: ResearchQuery, db: Session = Depends(get_db)):
    """Process a research query and return enhanced research results with all features."""
    
    try:
        # Use MCP client to search for papers
        papers_data = await mcp_client.search_papers(query.prompt, max_results=10)
        papers = []
        
        if "papers" in papers_data:
            for paper_data in papers_data["papers"]:
                papers.append(ResearchPaper(**paper_data))
        
        # Generate workspace if requested
        workspace = None
        if query.include_workspace:
            workspace_data = await mcp_client.generate_workspace(query.prompt)
            workspace = ResearchWorkspace(**workspace_data)
        
        # Generate mindmap if requested
        mindmap = None
        if query.include_mindmap:
            mindmap_data = await mcp_client.create_mindmap(query.prompt)
            mindmap = InteractiveMindmap(**mindmap_data)
        
        # Generate comprehensive summaries if requested
        summaries = None
        if query.include_summaries:
            summaries = generate_comprehensive_summaries(query.prompt, papers)
        
        # Generate automated citations if requested
        citations = None
        if query.include_citations:
            citations = generate_automated_citations(papers)
        
        # Generate sample research paper if requested
        sample_paper = None
        if query.include_sample_paper:
            sample_paper = generate_sample_research_paper(query.prompt, papers)
        
        # Generate mock audio URL if requested
        audio_url = "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA..." if query.include_audio else None
        
        return EnhancedResearchResponse(
            papers=papers,
            workspace=workspace,
            interactive_mindmap=mindmap,
            comprehensive_summaries=summaries,
            automated_citations=citations,
            sample_paper=sample_paper,
            audio_url=audio_url
        )
        
    except Exception as e:
        logger.error(f"Research query error: {e}")
        # Fallback to mock data if MCP fails
        return await research_query_fallback(query, db)


# Individual Feature Endpoints

@app.post("/api/research/mindmap", response_model=InteractiveMindmap)
async def generate_research_mindmap(request: dict, db: Session = Depends(get_db)):
    """Generate an interactive mind map for a research topic."""
    topic = request.get("topic", "")
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    
    try:
        mindmap_data = await mcp_client.create_mindmap(topic)
        return InteractiveMindmap(**mindmap_data)
    except Exception as e:
        logger.error(f"Mindmap generation error: {e}")
        return generate_mock_mindmap(topic)


@app.post("/api/research/summaries", response_model=ComprehensiveSummaries)
async def generate_research_summaries(request: dict, db: Session = Depends(get_db)):
    """Generate comprehensive summaries for a research topic."""
    topic = request.get("topic", "")
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    
    try:
        # Get papers for the topic
        papers_data = await mcp_client.search_papers(topic, max_results=10)
        papers = []
        if "papers" in papers_data:
            for paper_data in papers_data["papers"]:
                papers.append(ResearchPaper(**paper_data))
        else:
            # Use mock papers if MCP fails
            papers = [ResearchPaper(**paper) for paper in MOCK_RESEARCH_PAPERS[:5]]
        
        return generate_comprehensive_summaries(topic, papers)
    except Exception as e:
        logger.error(f"Summaries generation error: {e}")
        papers = [ResearchPaper(**paper) for paper in MOCK_RESEARCH_PAPERS[:5]]
        return generate_comprehensive_summaries(topic, papers)


@app.post("/api/research/citations", response_model=AutomatedCitations)
async def generate_research_citations(request: dict, db: Session = Depends(get_db)):
    """Generate automated IEEE citations and bibliography."""
    topic = request.get("topic", "")
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    
    try:
        # Get papers for the topic
        papers_data = await mcp_client.search_papers(topic, max_results=10)
        papers = []
        if "papers" in papers_data:
            for paper_data in papers_data["papers"]:
                papers.append(ResearchPaper(**paper_data))
        else:
            papers = [ResearchPaper(**paper) for paper in MOCK_RESEARCH_PAPERS]
        
        return generate_automated_citations(papers)
    except Exception as e:
        logger.error(f"Citations generation error: {e}")
        papers = [ResearchPaper(**paper) for paper in MOCK_RESEARCH_PAPERS]
        return generate_automated_citations(papers)


@app.post("/api/research/sample-paper", response_model=SampleResearchPaper)
async def generate_research_paper(request: dict, db: Session = Depends(get_db)):
    """Generate a sample research paper based on the topic."""
    topic = request.get("topic", "")
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    
    try:
        # Get papers for the topic
        papers_data = await mcp_client.search_papers(topic, max_results=10)
        papers = []
        if "papers" in papers_data:
            for paper_data in papers_data["papers"]:
                papers.append(ResearchPaper(**paper_data))
        else:
            papers = [ResearchPaper(**paper) for paper in MOCK_RESEARCH_PAPERS]
        
        return generate_sample_research_paper(topic, papers)
    except Exception as e:
        logger.error(f"Sample paper generation error: {e}")
        papers = [ResearchPaper(**paper) for paper in MOCK_RESEARCH_PAPERS]
        return generate_sample_research_paper(topic, papers)


@app.get("/api/research/papers/{paper_id}/summary")
async def get_paper_summary(paper_id: int, db: Session = Depends(get_db)):
    """Get detailed summary for a specific research paper."""
    # Find paper in mock data (in real implementation, would query database)
    paper_data = None
    for paper in MOCK_RESEARCH_PAPERS:
        if paper["id"] == paper_id:
            paper_data = paper
            break
    
    if not paper_data:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    paper = ResearchPaper(**paper_data)
    summary = DocumentSummary(
        paper_id=paper.id,
        title=paper.title,
        summary=f"This comprehensive analysis of '{paper.title}' reveals significant contributions to the field. The research addresses key challenges and presents innovative solutions with practical applications.",
        key_findings=[
            f"Novel algorithm achieving {85 + paper_id}% improvement",
            "Comprehensive experimental validation",
            "Real-world application demonstration",
            "Theoretical framework establishment"
        ],
        methodology="The research employs a systematic approach combining theoretical analysis with empirical validation through controlled experiments and real-world testing.",
        limitations=[
            "Limited dataset size for certain experiments",
            "Computational complexity considerations",
            "Scope limitations to specific domains",
            "Need for longitudinal validation"
        ],
        significance="This work makes substantial contributions to the field by introducing novel methodologies and demonstrating their effectiveness across multiple application domains."
    )
    
    return summary
