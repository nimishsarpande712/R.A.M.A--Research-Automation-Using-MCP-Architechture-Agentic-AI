from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import logging
import asyncio

from .core import config
from .db.session import get_db
from .schemas.auth import UserLogin, Token, UserRegister, UserOut
from .db import models  # Assuming a models module exists
from .db.session import engine
from .mcp_client import mcp_client

logger = logging.getLogger(__name__)

# Research-related Pydantic models
class ResearchQuery(BaseModel):
    prompt: str
    include_workspace: bool = True
    include_mindmap: bool = True
    include_audio: bool = True

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

class MindmapNode(BaseModel):
    id: int
    label: str
    x: float
    y: float
    type: str

class MindmapConnection(BaseModel):
    from_id: int = Field(alias="from")
    to_id: int = Field(alias="to")

    class Config:
        allow_population_by_field_name = True

class ResearchMindmap(BaseModel):
    id: str
    topic: str
    nodes: List[MindmapNode]
    connections: List[MindmapConnection]

class ResearchResponse(BaseModel):
    papers: List[ResearchPaper]
    workspace: Optional[ResearchWorkspace] = None
    mindmap: Optional[ResearchMindmap] = None
    audio_url: Optional[str] = None

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


def generate_mock_mindmap(topic: str) -> ResearchMindmap:
    """Generate a mock research mindmap based on the topic."""
    return ResearchMindmap(
        id=f"mm_{int(datetime.now().timestamp())}",
        topic=topic,
        nodes=[
            MindmapNode(id=1, label=topic, x=300, y=200, type='central'),
            MindmapNode(id=2, label="Key Concepts", x=150, y=100, type='main'),
            MindmapNode(id=3, label="Applications", x=450, y=100, type='main'),
            MindmapNode(id=4, label="Challenges", x=150, y=300, type='main'),
            MindmapNode(id=5, label="Future Directions", x=450, y=300, type='main'),
            MindmapNode(id=6, label="Algorithms", x=100, y=50, type='sub'),
            MindmapNode(id=7, label="Optimization", x=200, y=50, type='sub'),
            MindmapNode(id=8, label="Real-world Uses", x=400, y=50, type='sub'),
            MindmapNode(id=9, label="Industry Applications", x=500, y=50, type='sub'),
        ],
        connections=[
            MindmapConnection(from_id=1, to_id=2),
            MindmapConnection(from_id=1, to_id=3),
            MindmapConnection(from_id=1, to_id=4),
            MindmapConnection(from_id=1, to_id=5),
            MindmapConnection(from_id=2, to_id=6),
            MindmapConnection(from_id=2, to_id=7),
            MindmapConnection(from_id=3, to_id=8),
            MindmapConnection(from_id=3, to_id=9)
        ]
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
    
    # Generate mock audio URL if requested
    audio_url = "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA..." if query.include_audio else None
    
    return ResearchResponse(
        papers=papers,
        workspace=workspace,
        mindmap=mindmap,
        audio_url=audio_url
    )


@app.post("/api/research/query", response_model=ResearchResponse)
async def research_query(query: ResearchQuery, db: Session = Depends(get_db)):
    """Process a research query and return relevant papers, workspace, mindmap, and audio."""
    
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
            mindmap = ResearchMindmap(**mindmap_data)
        
        # Generate mock audio URL if requested
        audio_url = "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA..." if query.include_audio else None
        
        return ResearchResponse(
            papers=papers,
            workspace=workspace,
            mindmap=mindmap,
            audio_url=audio_url
        )
        
    except Exception as e:
        logger.error(f"Research query error: {e}")
        # Fallback to mock data if MCP fails
        return await research_query_fallback(query, db)
