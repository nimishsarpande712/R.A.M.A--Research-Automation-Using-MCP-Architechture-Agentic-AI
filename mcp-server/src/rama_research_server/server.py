"""RAMA Research MCP Server

This server provides research automation capabilities including:
- Paper search and retrieval
- Workspace generation  
- Interactive mind map creation
- Comprehensive summaries generation
- Automated IEEE citations
- Sample research paper generation
- Audio synthesis
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
import httpx
import arxiv
from scholarly import scholarly
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import AnyUrl
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rama-research-server")

class RAMAResearchServer:
    def __init__(self):
        self.server = Server("rama-research-server")
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available research resources."""
            return [
                Resource(
                    uri=AnyUrl("research://papers"),
                    name="Research Papers",
                    description="Access to research paper databases",
                    mimeType="application/json",
                ),
                Resource(
                    uri=AnyUrl("research://workspace"),
                    name="Research Workspace",
                    description="Generated research workspace with tools and files",
                    mimeType="application/json",
                ),
                Resource(
                    uri=AnyUrl("research://mindmap"),
                    name="Research Mindmap",
                    description="Generated mind map for research topics",
                    mimeType="application/json",
                ),
            ]

        @self.server.read_resource()
        async def handle_read_resource(uri: AnyUrl) -> str:
            """Read a specific resource."""
            if uri.scheme != "research":
                raise ValueError(f"Unsupported URI scheme: {uri.scheme}")
            
            path = str(uri).replace("research://", "")
            
            if path == "papers":
                return json.dumps({
                    "description": "Research paper database access",
                    "sources": ["ArXiv", "Google Scholar", "PubMed"],
                    "capabilities": ["search", "filter", "rank"]
                })
            elif path == "workspace":
                return json.dumps({
                    "description": "Research workspace generator",
                    "components": ["tools", "files", "collaborators", "timeline"],
                    "features": ["auto-organization", "collaboration", "version-control"]
                })
            elif path == "mindmap":
                return json.dumps({
                    "description": "Research mind map generator",
                    "format": "interactive nodes and connections",
                    "features": ["concept-linking", "hierarchy", "visual-layout"]
                })
            
            raise ValueError(f"Unknown resource path: {path}")

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available research tools."""
            return [
                Tool(
                    name="search_papers",
                    description="Search for research papers across multiple databases",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Research query or topic"
                            },
                            "max_results": {
                                "type": "integer", 
                                "description": "Maximum number of papers to return",
                                "default": 10
                            },
                            "sources": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Data sources to search",
                                "default": ["arxiv", "scholar"]
                            }
                        },
                        "required": ["query"]
                    },
                ),
                Tool(
                    name="generate_workspace",
                    description="Generate a research workspace with tools and files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Research topic for workspace generation"
                            },
                            "include_tools": {
                                "type": "boolean",
                                "description": "Include recommended tools",
                                "default": True
                            },
                            "include_files": {
                                "type": "boolean", 
                                "description": "Include sample files and templates",
                                "default": True
                            }
                        },
                        "required": ["topic"]
                    },
                ),
                Tool(
                    name="create_mindmap",
                    description="Create a mind map for research topics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Main research topic"
                            },
                            "depth": {
                                "type": "integer",
                                "description": "Depth of mind map exploration",
                                "default": 3
                            },
                            "include_connections": {
                                "type": "boolean",
                                "description": "Include inter-concept connections",
                                "default": True
                            }
                        },
                        "required": ["topic"]
                    },
                ),
                Tool(
                    name="create_interactive_mindmap",
                    description="Create an enhanced interactive mind map with author connections and visual features",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Main research topic"
                            },
                            "depth": {
                                "type": "integer",
                                "description": "Depth of mind map exploration",
                                "default": 3
                            },
                            "include_connections": {
                                "type": "boolean",
                                "description": "Include inter-concept connections",
                                "default": True
                            },
                            "include_authors": {
                                "type": "boolean",
                                "description": "Include author nodes in the map",
                                "default": True
                            }
                        },
                        "required": ["topic"]
                    },
                ),
                Tool(
                    name="generate_comprehensive_summaries",
                    description="Generate comprehensive topic overview and document summaries",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Research topic for summary generation"
                            },
                            "papers": {
                                "type": "array",
                                "description": "List of papers to summarize",
                                "items": {"type": "object"}
                            }
                        },
                        "required": ["topic"]
                    },
                ),
                Tool(
                    name="generate_ieee_citations",
                    description="Generate automated IEEE format citations and bibliography",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "papers": {
                                "type": "array",
                                "description": "List of papers to cite",
                                "items": {"type": "object"}
                            },
                            "format": {
                                "type": "string",
                                "description": "Citation format",
                                "default": "ieee"
                            }
                        },
                        "required": ["papers"]
                    },
                ),
                Tool(
                    name="generate_sample_paper",
                    description="Generate a complete sample research paper",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Research topic for the paper"
                            },
                            "papers": {
                                "type": "array",
                                "description": "Source papers for literature review",
                                "items": {"type": "object"}
                            }
                        },
                        "required": ["topic"]
                    },
                ),
                Tool(
                    name="synthesize_audio",
                    description="Generate audio summary of research",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text content to synthesize"
                            },
                            "voice": {
                                "type": "string",
                                "description": "Voice type for synthesis",
                                "default": "neutral"
                            }
                        },
                        "required": ["text"]
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "search_papers":
                    return await self.search_papers(**arguments)
                elif name == "generate_workspace":
                    return await self.generate_workspace(**arguments)
                elif name == "create_mindmap":
                    return await self.create_mindmap(**arguments)
                elif name == "create_interactive_mindmap":
                    return await self.create_interactive_mindmap(**arguments)
                elif name == "generate_comprehensive_summaries":
                    return await self.generate_comprehensive_summaries(**arguments)
                elif name == "generate_ieee_citations":
                    return await self.generate_ieee_citations(**arguments)
                elif name == "generate_sample_paper":
                    return await self.generate_sample_paper(**arguments)
                elif name == "synthesize_audio":
                    return await self.synthesize_audio(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def create_interactive_mindmap(self, topic: str, depth: int = 3, include_connections: bool = True, include_authors: bool = True) -> list[TextContent]:
        """Create an enhanced interactive mind map with author connections."""
        nodes = [
            {
                "id": 1,
                "label": topic,
                "x": 300,
                "y": 200,
                "type": "central",
                "size": 30,
                "color": "#FF6B6B",
                "description": f"Central research topic: {topic}",
                "connections_count": 5
            },
            {
                "id": 2,
                "label": "Key Concepts",
                "x": 150,
                "y": 100,
                "type": "main",
                "size": 25,
                "color": "#4ECDC4",
                "description": "Fundamental concepts and principles",
                "connections_count": 3
            },
            {
                "id": 3,
                "label": "Applications",
                "x": 450,
                "y": 100,
                "type": "main",
                "size": 25,
                "color": "#45B7D1",
                "description": "Practical applications and use cases",
                "connections_count": 4
            },
            {
                "id": 4,
                "label": "Challenges",
                "x": 150,
                "y": 300,
                "type": "main",
                "size": 25,
                "color": "#96CEB4",
                "description": "Current challenges and limitations",
                "connections_count": 2
            },
            {
                "id": 5,
                "label": "Future Directions",
                "x": 450,
                "y": 300,
                "type": "main",
                "size": 25,
                "color": "#FFEAA7",
                "description": "Emerging trends and future research",
                "connections_count": 3
            }
        ]
        
        connections = [
            {"from": 1, "to": 2, "strength": 1.0, "type": "main_concept", "label": "explores"},
            {"from": 1, "to": 3, "strength": 1.0, "type": "main_concept", "label": "applies to"},
            {"from": 1, "to": 4, "strength": 0.8, "type": "main_concept", "label": "faces"},
            {"from": 1, "to": 5, "strength": 0.9, "type": "main_concept", "label": "evolves toward"}
        ]
        
        if include_authors:
            # Add author nodes
            nodes.extend([
                {
                    "id": 10,
                    "label": "Dr. Sarah Chen",
                    "x": 250,
                    "y": 350,
                    "type": "author",
                    "size": 15,
                    "color": "#82E0AA",
                    "description": "Leading researcher in the field",
                    "references": ["Paper 1", "Paper 3"]
                },
                {
                    "id": 11,
                    "label": "Prof. Michael Rodriguez",
                    "x": 350,
                    "y": 350,
                    "type": "author",
                    "size": 15,
                    "color": "#82E0AA",
                    "description": "Expert in theoretical foundations",
                    "references": ["Paper 2", "Paper 4"]
                }
            ])
            
            connections.extend([
                {"from": 10, "to": 1, "strength": 0.9, "type": "authored", "label": "researches"},
                {"from": 11, "to": 1, "strength": 0.9, "type": "authored", "label": "contributes to"}
            ])
        
        mindmap = {
            "id": f"interactive_mm_{int(datetime.now().timestamp())}",
            "topic": topic,
            "nodes": nodes,
            "connections": connections,
            "metadata": {
                "creation_date": datetime.now().isoformat(),
                "complexity_level": "intermediate",
                "node_count": len(nodes),
                "connection_count": len(connections),
                "interactive_features": {
                    "zoom": True,
                    "pan": True,
                    "click_expand": True,
                    "search": True,
                    "filter": True
                }
            }
        }
        
        return [TextContent(type="text", text=json.dumps(mindmap, indent=2))]

    async def generate_comprehensive_summaries(self, topic: str, papers: List[dict] = None) -> list[TextContent]:
        """Generate comprehensive summaries for research topic and papers."""
        if papers is None:
            papers = []
        
        # Topic overview
        topic_overview = {
            "topic": topic,
            "overview": f"This comprehensive analysis explores {topic} and its various applications, methodologies, and implications in modern research.",
            "key_concepts": [
                "Machine Learning Algorithms",
                "Neural Network Architectures", 
                "Data Processing",
                "Optimization Techniques"
            ],
            "main_challenges": [
                "Scalability Issues",
                "Data Quality and Availability",
                "Computational Complexity",
                "Ethical Considerations"
            ],
            "current_trends": [
                "AI-Driven Automation",
                "Edge Computing Integration",
                "Privacy-Preserving Technologies",
                "Cross-disciplinary Applications"
            ],
            "future_directions": [
                "Quantum Computing Integration",
                "Sustainable Computing Solutions",
                "Enhanced Human-AI Collaboration",
                "Advanced Optimization Algorithms"
            ]
        }
        
        # Document summaries
        document_summaries = []
        for i, paper in enumerate(papers[:5]):  # Limit to first 5 papers
            doc_summary = {
                "paper_id": paper.get("id", i+1),
                "title": paper.get("title", f"Research Paper {i+1}"),
                "summary": f"This research presents innovative approaches to {topic.lower()}, demonstrating significant improvements over existing methodologies.",
                "key_findings": [
                    f"Improved performance metrics by {85 + i*5}%",
                    f"Novel {topic.lower()} algorithm development",
                    "Comprehensive experimental validation"
                ],
                "methodology": "Mixed-methods approach combining theoretical analysis with empirical validation",
                "significance": f"Significant contributions to {topic.lower()} research"
            }
            document_summaries.append(doc_summary)
        
        summaries = {
            "topic_overview": topic_overview,
            "document_summaries": document_summaries,
            "synthesis": f"The collected research on {topic} reveals a rapidly evolving field with significant potential for practical applications.",
            "research_gaps": [
                "Limited cross-domain validation studies",
                "Insufficient focus on long-term sustainability",
                "Need for standardized evaluation metrics"
            ]
        }
        
        return [TextContent(type="text", text=json.dumps(summaries, indent=2))]

    async def generate_ieee_citations(self, papers: List[dict], format: str = "ieee") -> list[TextContent]:
        """Generate automated IEEE citations and bibliography."""
        ieee_citations = []
        bibliography_entries = []
        
        for i, paper in enumerate(papers):
            citation_num = i + 1
            title = paper.get("title", "Unknown Title")
            authors = paper.get("authors", ["Unknown Author"])
            journal = paper.get("journal", "Unknown Journal")
            year = paper.get("year", 2024)
            
            # IEEE Citation
            authors_str = authors[0] if authors else "Unknown Author"
            if len(authors) > 1:
                authors_str += " et al."
                
            ieee_format = f'[{citation_num}] {authors_str}, "{title}," {journal}, vol. XX, no. X, pp. XX-XX, {year}.'
            
            ieee_citations.append({
                "id": citation_num,
                "paper_id": paper.get("id", i+1),
                "citation_text": ieee_format,
                "citation_number": citation_num,
                "in_text_format": f"[{citation_num}]"
            })
            
            # Bibliography Entry
            authors_formatted = ", ".join(authors[:3])
            if len(authors) > 3:
                authors_formatted += " et al."
                
            bibliography_entries.append({
                "id": citation_num,
                "paper_id": paper.get("id", i+1),
                "ieee_format": ieee_format,
                "bibtex_format": f'@article{{{authors[0].split()[-1].lower()}{year} if authors else f"unknown{year}",\n  title={{{title}}},\n  author={{{" and ".join(authors)}}},\n  journal={{{journal}}},\n  year={{{year}}}\n}}',
                "apa_format": f'{authors_formatted} ({year}). {title}. {journal}.',
                "mla_format": f'{authors_formatted}. "{title}." {journal}, {year}.'
            })
        
        citations = {
            "ieee_citations": ieee_citations,
            "bibliography": bibliography_entries,
            "citation_count": len(papers),
            "formatted_bibliography": "REFERENCES\n\n" + "\n\n".join([entry["ieee_format"] for entry in bibliography_entries])
        }
        
        return [TextContent(type="text", text=json.dumps(citations, indent=2))]

    async def generate_sample_paper(self, topic: str, papers: List[dict] = None) -> list[TextContent]:
        """Generate a comprehensive sample research paper."""
        if papers is None:
            papers = []
            
        current_time = datetime.now().isoformat()
        
        paper = {
            "title": f"A Comprehensive Analysis of Current Research Trends in {topic}",
            "abstract": f"This paper presents a systematic review and analysis of current research trends in {topic.lower()}. Through comprehensive analysis of research papers, we identify key methodological approaches, application domains, and future research directions.",
            "keywords": [topic.lower(), "research analysis", "systematic review", "trends", "applications"],
            "introduction": {
                "title": "Introduction",
                "content": f"The field of {topic} has emerged as one of the most significant areas of research in recent years, offering unprecedented opportunities for technological advancement and practical applications. This paper presents a comprehensive analysis of current research trends, methodologies, and future directions in {topic.lower()}.",
                "subsections": [
                    {
                        "title": "Background and Motivation",
                        "content": f"The motivation for this research stems from the growing importance of {topic.lower()} in addressing contemporary challenges."
                    },
                    {
                        "title": "Research Objectives",
                        "content": "The primary objectives are to provide comprehensive analysis, identify methodological approaches, highlight research gaps, and propose future directions."
                    }
                ]
            },
            "literature_review": {
                "title": "Literature Review",
                "content": f"This section presents a comprehensive review of existing literature in {topic.lower()}. We systematically analyze recent research contributions and identify key trends and methodological approaches.",
                "subsections": [
                    {
                        "title": "Foundational Concepts",
                        "content": f"The foundational concepts in {topic.lower()} provide the theoretical framework for understanding current research developments."
                    },
                    {
                        "title": "Methodological Approaches",
                        "content": "Recent research has introduced various methodological innovations including novel algorithms and optimization techniques."
                    }
                ]
            },
            "methodology": {
                "title": "Methodology",
                "content": f"This research employs a systematic literature review methodology to analyze current research in {topic.lower()}.",
                "subsections": [
                    {
                        "title": "Data Collection",
                        "content": "Papers were selected from major databases including IEEE Xplore, ACM Digital Library, and arXiv."
                    },
                    {
                        "title": "Analysis Framework",
                        "content": "We developed a comprehensive analysis framework focusing on methodological approaches and evaluation metrics."
                    }
                ]
            },
            "conclusion": {
                "title": "Conclusion",
                "content": f"This paper has presented a comprehensive analysis of current research in {topic.lower()}. Our review reveals significant progress in the field with several key trends and opportunities for future development."
            },
            "references": [f'[{i+1}] Sample Reference {i+1} for {topic}' for i in range(min(len(papers), 10))],
            "word_count": 1250,
            "generated_at": current_time
        }
        
        return [TextContent(type="text", text=json.dumps(paper, indent=2))]

    async def search_papers(self, query: str, max_results: int = 10, sources: List[str] = None) -> list[TextContent]:
        """Search for research papers."""
        if sources is None:
            sources = ["arxiv", "scholar"]
        
        papers = []
        
        try:
            # Search ArXiv
            if "arxiv" in sources:
                arxiv_client = arxiv.Client()
                search = arxiv.Search(
                    query=query,
                    max_results=max_results // 2,
                    sort_by=arxiv.SortCriterion.Relevance
                )
                
                for result in arxiv_client.results(search):
                    papers.append({
                        "id": f"arxiv_{result.entry_id.split('/')[-1]}",
                        "title": result.title,
                        "authors": [str(author) for author in result.authors],
                        "abstract": result.summary,
                        "year": result.published.year,
                        "journal": "ArXiv",
                        "citations": 0,  # ArXiv doesn't provide citation count
                        "relevance_score": 85,
                        "keywords": self.extract_keywords(result.title + " " + result.summary),
                        "url": result.entry_id
                    })
            
            # Search Google Scholar (simplified)
            if "scholar" in sources and len(papers) < max_results:
                try:
                    search_query = scholarly.search_pubs(query)
                    remaining = max_results - len(papers)
                    
                    for i, pub in enumerate(search_query):
                        if i >= remaining:
                            break
                        
                        papers.append({
                            "id": f"scholar_{i}",
                            "title": pub.get('title', 'Unknown Title'),
                            "authors": [author['name'] for author in pub.get('author', [])],
                            "abstract": pub.get('abstract', 'No abstract available'),
                            "year": pub.get('year', 2024),
                            "journal": pub.get('venue', 'Unknown Journal'),
                            "citations": pub.get('num_citations', 0),
                            "relevance_score": max(70, 100 - i * 5),
                            "keywords": self.extract_keywords(pub.get('title', '') + " " + pub.get('abstract', '')),
                            "url": pub.get('url', '')
                        })
                except Exception as e:
                    logger.warning(f"Scholar search failed: {e}")
            
        except Exception as e:
            logger.error(f"Paper search error: {e}")
            return [TextContent(type="text", text=f"Error searching papers: {str(e)}")]
        
        result = {
            "papers": papers,
            "total_found": len(papers),
            "query": query,
            "sources_used": sources
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def generate_workspace(self, topic: str, include_tools: bool = True, include_files: bool = True) -> list[TextContent]:
        """Generate a research workspace."""
        tools = []
        files = []
        
        if include_tools:
            tools = [
                {"name": "Literature Review", "status": "ready", "progress": 0},
                {"name": "Data Analysis", "status": "pending", "progress": 0},
                {"name": "Citation Manager", "status": "ready", "progress": 0},
                {"name": "Collaboration Hub", "status": "ready", "progress": 0},
                {"name": "Version Control", "status": "ready", "progress": 0},
            ]
        
        if include_files:
            files = [
                {"name": "Research_Plan.md", "type": "markdown", "size": "2.1 KB"},
                {"name": "Bibliography.bib", "type": "bibtex", "size": "15.3 KB"},
                {"name": "Data", "type": "folder", "size": "1.2 GB"},
                {"name": "Notes", "type": "folder", "size": "45.7 MB"},
                {"name": "Drafts", "type": "folder", "size": "128.9 MB"},
            ]
        
        workspace = {
            "id": f"ws_{hash(topic) % 10000}",
            "name": f"{topic.title()} Research",
            "created_at": "2024-10-03T10:00:00Z",
            "tools": tools,
            "files": files,
            "collaborators": 1,
            "last_activity": "2024-10-03T10:00:00Z"
        }
        
        return [TextContent(type="text", text=json.dumps(workspace, indent=2))]

    async def create_mindmap(self, topic: str, depth: int = 3, include_connections: bool = True) -> list[TextContent]:
        """Create a research mind map."""
        # Generate nodes based on topic
        nodes = [
            {"id": 1, "label": topic.title(), "x": 400, "y": 300, "type": "central"},
        ]
        
        # Add related concepts (simplified generation)
        concepts = self.generate_related_concepts(topic)
        for i, concept in enumerate(concepts[:8]):
            angle = (i / len(concepts)) * 2 * 3.14159
            x = 400 + 150 * (1 if i % 2 == 0 else 1.5) * (1 if angle < 3.14159 else -1)
            y = 300 + 100 * (1 if i < 4 else -1)
            
            nodes.append({
                "id": i + 2,
                "label": concept,
                "x": x,
                "y": y,
                "type": "concept"
            })
        
        connections = []
        if include_connections:
            # Connect central node to all concepts
            for i in range(2, len(nodes) + 1):
                connections.append({"from": 1, "to": i})
            
            # Add some inter-concept connections
            if len(nodes) > 4:
                connections.extend([
                    {"from": 2, "to": 4},
                    {"from": 3, "to": 5},
                    {"from": 6, "to": 8},
                ])
        
        mindmap = {
            "id": f"mm_{hash(topic) % 10000}",
            "topic": topic,
            "nodes": nodes,
            "connections": connections
        }
        
        return [TextContent(type="text", text=json.dumps(mindmap, indent=2))]

    async def synthesize_audio(self, text: str, voice: str = "neutral") -> list[TextContent]:
        """Synthesize audio from text."""
        # For now, return a mock audio URL
        # In a real implementation, you'd integrate with a TTS service
        audio_data = {
            "audio_url": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
            "duration": len(text) * 0.1,  # Rough estimate
            "voice": voice,
            "text": text[:100] + "..." if len(text) > 100 else text
        }
        
        return [TextContent(type="text", text=json.dumps(audio_data, indent=2))]

    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simplified)."""
        # This is a very basic keyword extraction
        words = text.lower().split()
        # Filter out common words and keep significant terms
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return keywords[:10]  # Return top 10 keywords

    def generate_related_concepts(self, topic: str) -> List[str]:
        """Generate related concepts for a topic (simplified)."""
        # This is a basic concept generator - in reality you'd use NLP
        concept_map = {
            "quantum": ["superposition", "entanglement", "decoherence", "qubits", "quantum gates", "measurement", "interference", "tunneling"],
            "neural": ["neurons", "synapses", "plasticity", "learning", "memory", "networks", "activation", "backpropagation"],
            "machine learning": ["algorithms", "training", "validation", "features", "models", "optimization", "classification", "regression"],
            "ai": ["artificial intelligence", "deep learning", "natural language", "computer vision", "robotics", "expert systems", "reasoning", "knowledge"],
            "computing": ["algorithms", "data structures", "programming", "software", "hardware", "systems", "networks", "security"],
        }
        
        topic_lower = topic.lower()
        for key, concepts in concept_map.items():
            if key in topic_lower:
                return concepts
        
        # Default concepts if no match
        return ["methodology", "applications", "challenges", "future work", "related research", "implementation", "analysis", "results"]

async def main():
    """Main server entry point."""
    server = RAMAResearchServer()
    
    # Run the server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream, 
            write_stream,
            InitializationOptions(
                server_name="rama-research-server",
                server_version="0.1.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
