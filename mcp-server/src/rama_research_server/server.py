"""RAMA Research MCP Server

This server provides research automation capabilities including:
- Paper search and retrieval
- Workspace generation  
- Mind map creation
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
                elif name == "synthesize_audio":
                    return await self.synthesize_audio(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

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
