"""MCP Client integration for RAMA backend."""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for communicating with RAMA Research MCP Server."""
    
    def __init__(self):
        self.process = None
        self.initialized = False
    
    async def start(self):
        """Start the MCP server process."""
        try:
            # Start the MCP server as a subprocess
            cmd = [sys.executable, "-m", "rama_research_server.server"]
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="../mcp-server"
            )
            
            # Initialize the connection
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "resources": {},
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "rama-backend",
                        "version": "0.1.0"
                    }
                }
            }
            
            await self._send_request(init_request)
            response = await self._read_response()
            
            if response and response.get("result"):
                self.initialized = True
                logger.info("MCP Server initialized successfully")
            else:
                logger.error(f"MCP Server initialization failed: {response}")
                
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            self.initialized = False
    
    async def stop(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
            self.initialized = False
    
    async def _send_request(self, request: Dict[str, Any]):
        """Send a JSON-RPC request to the MCP server."""
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP server not started")
        
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()
    
    async def _read_response(self) -> Optional[Dict[str, Any]]:
        """Read a JSON-RPC response from the MCP server."""
        if not self.process or not self.process.stdout:
            return None
        
        try:
            line = await self.process.stdout.readline()
            if line:
                return json.loads(line.decode().strip())
        except Exception as e:
            logger.error(f"Error reading MCP response: {e}")
        
        return None
    
    async def search_papers(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search for research papers using MCP server."""
        if not self.initialized:
            await self.start()
        
        if not self.initialized:
            # Fallback to mock data if MCP server fails
            return self._get_mock_papers(query)
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "search_papers",
                    "arguments": {
                        "query": query,
                        "max_results": max_results,
                        "sources": ["arxiv", "scholar"]
                    }
                }
            }
            
            await self._send_request(request)
            response = await self._read_response()
            
            if response and response.get("result"):
                content = response["result"].get("content", [])
                if content and content[0].get("type") == "text":
                    result_data = json.loads(content[0]["text"])
                    return result_data
            
        except Exception as e:
            logger.error(f"MCP paper search failed: {e}")
        
        # Fallback to mock data
        return self._get_mock_papers(query)
    
    async def generate_workspace(self, topic: str) -> Dict[str, Any]:
        """Generate research workspace using MCP server."""
        if not self.initialized:
            await self.start()
        
        if not self.initialized:
            return self._get_mock_workspace(topic)
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "generate_workspace",
                    "arguments": {
                        "topic": topic,
                        "include_tools": True,
                        "include_files": True
                    }
                }
            }
            
            await self._send_request(request)
            response = await self._read_response()
            
            if response and response.get("result"):
                content = response["result"].get("content", [])
                if content and content[0].get("type") == "text":
                    return json.loads(content[0]["text"])
            
        except Exception as e:
            logger.error(f"MCP workspace generation failed: {e}")
        
        return self._get_mock_workspace(topic)
    
    async def create_mindmap(self, topic: str) -> Dict[str, Any]:
        """Create research mindmap using MCP server."""
        if not self.initialized:
            await self.start()
        
        if not self.initialized:
            return self._get_mock_mindmap(topic)
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "create_mindmap",
                    "arguments": {
                        "topic": topic,
                        "depth": 3,
                        "include_connections": True
                    }
                }
            }
            
            await self._send_request(request)
            response = await self._read_response()
            
            if response and response.get("result"):
                content = response["result"].get("content", [])
                if content and content[0].get("type") == "text":
                    return json.loads(content[0]["text"])
            
        except Exception as e:
            logger.error(f"MCP mindmap creation failed: {e}")
        
        return self._get_mock_mindmap(topic)
    
    async def generate_comprehensive_summaries(self, query: str, papers: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive summaries using MCP server."""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "generate_comprehensive_summaries",
                    "arguments": {
                        "query": query,
                        "papers": papers
                    }
                }
            }
            
            await self._send_request(request)
            response = await self._read_response()
            
            if response and response.get("result"):
                return response["result"]["content"][0]["text"]
            
        except Exception as e:
            logger.error(f"MCP comprehensive summaries generation failed: {e}")
        
        return self._get_mock_summaries(query, papers)
    
    async def generate_ieee_citations(self, papers: List[Dict]) -> Dict[str, Any]:
        """Generate IEEE citations using MCP server."""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "generate_ieee_citations",
                    "arguments": {
                        "papers": papers
                    }
                }
            }
            
            await self._send_request(request)
            response = await self._read_response()
            
            if response and response.get("result"):
                return response["result"]["content"][0]["text"]
            
        except Exception as e:
            logger.error(f"MCP IEEE citations generation failed: {e}")
        
        return self._get_mock_citations(papers)
    
    async def generate_sample_paper(self, query: str, papers: List[Dict]) -> Dict[str, Any]:
        """Generate sample research paper using MCP server."""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "generate_sample_paper",
                    "arguments": {
                        "query": query,
                        "papers": papers
                    }
                }
            }
            
            await self._send_request(request)
            response = await self._read_response()
            
            if response and response.get("result"):
                return response["result"]["content"][0]["text"]
            
        except Exception as e:
            logger.error(f"MCP sample paper generation failed: {e}")
        
        return self._get_mock_sample_paper(query, papers)
    
    async def create_interactive_mindmap(self, query: str, papers: List[Dict]) -> Dict[str, Any]:
        """Create interactive mindmap using MCP server."""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "create_interactive_mindmap",
                    "arguments": {
                        "query": query,
                        "papers": papers
                    }
                }
            }
            
            await self._send_request(request)
            response = await self._read_response()
            
            if response and response.get("result"):
                return response["result"]["content"][0]["text"]
            
        except Exception as e:
            logger.error(f"MCP interactive mindmap creation failed: {e}")
        
        return self._get_mock_interactive_mindmap(query, papers)
    
    def _get_mock_papers(self, query: str) -> Dict[str, Any]:
        """Fallback mock papers when MCP server is unavailable."""
        return {
            "papers": [
                {
                    "id": 1,
                    "title": f"Advanced Research in {query.title()}",
                    "authors": ["Dr. Jane Smith", "Prof. John Doe"],
                    "abstract": f"This paper explores the fundamental concepts and applications of {query} in modern research environments...",
                    "year": 2024,
                    "journal": "Nature",
                    "citations": 156,
                    "relevance_score": 95,
                    "keywords": [query.lower(), "research", "methodology", "analysis"]
                }
            ],
            "total_found": 1,
            "query": query,
            "sources_used": ["mock"]
        }
    
    def _get_mock_workspace(self, topic: str) -> Dict[str, Any]:
        """Fallback mock workspace."""
        return {
            "id": f"ws_{abs(hash(topic)) % 10000}",
            "name": f"{topic.title()} Research Workspace",
            "created_at": "2024-10-03T10:00:00Z",
            "tools": [
                {"name": "Literature Review", "status": "ready", "progress": 0},
                {"name": "Data Analysis", "status": "pending", "progress": 0},
                {"name": "Citation Manager", "status": "ready", "progress": 0}
            ],
            "files": [
                {"name": "Research_Plan.md", "type": "markdown", "size": "2.1 KB"},
                {"name": "Bibliography.bib", "type": "bibtex", "size": "15.3 KB"},
                {"name": "Data", "type": "folder", "size": "1.2 GB"}
            ],
            "collaborators": 1,
            "last_activity": "2024-10-03T10:00:00Z"
        }
    
    def _get_mock_mindmap(self, topic: str) -> Dict[str, Any]:
        """Fallback mock mindmap."""
        return {
            "id": f"mm_{abs(hash(topic)) % 10000}",
            "topic": topic,
            "nodes": [
                {"id": 1, "label": topic.title(), "x": 400, "y": 300, "type": "central"},
                {"id": 2, "label": "Methodology", "x": 300, "y": 200, "type": "concept"},
                {"id": 3, "label": "Applications", "x": 500, "y": 200, "type": "concept"},
                {"id": 4, "label": "Future Work", "x": 300, "y": 400, "type": "concept"},
                {"id": 5, "label": "Related Research", "x": 500, "y": 400, "type": "concept"}
            ],
            "connections": [
                {"from": 1, "to": 2},
                {"from": 1, "to": 3},
                {"from": 1, "to": 4},
                {"from": 1, "to": 5}
            ]
        }

    def _get_mock_summaries(self, query: str, papers: List[Dict]) -> Dict[str, Any]:
        """Fallback mock comprehensive summaries."""
        return {
            "id": f"summaries_{abs(hash(query)) % 10000}",
            "query": query,
            "topic_overview": f"This comprehensive analysis of {query} reveals significant developments in the field. Current research demonstrates strong progress in both theoretical foundations and practical applications.",
            "key_themes": [
                "Theoretical Foundations",
                "Methodological Advances", 
                "Practical Applications",
                "Future Directions"
            ],
            "document_summaries": [
                {
                    "paper_id": paper.get("id", 1),
                    "title": paper.get("title", "Sample Paper"),
                    "summary": f"This paper contributes to {query} by presenting novel approaches and methodologies...",
                    "key_findings": ["Novel methodology", "Improved results", "Significant implications"],
                    "relevance": paper.get("relevance_score", 85)
                } for paper in papers[:5]
            ],
            "research_gaps": [
                "Limited longitudinal studies",
                "Need for larger sample sizes", 
                "Cross-cultural validation required"
            ],
            "created_at": "2024-10-03T10:00:00Z"
        }

    def _get_mock_citations(self, papers: List[Dict]) -> Dict[str, Any]:
        """Fallback mock IEEE citations."""
        citations = []
        for i, paper in enumerate(papers[:10], 1):
            author_list = ", ".join(paper.get("authors", ["J. Smith", "A. Johnson"])[:3])
            if len(paper.get("authors", [])) > 3:
                author_list += " et al."
            
            citation = f'[{i}] {author_list}, "{paper.get("title", "Research Paper Title")}", {paper.get("journal", "IEEE Transactions")}, vol. X, no. Y, pp. 1-10, {paper.get("year", 2024)}.'
            citations.append({
                "number": i,
                "paper_id": paper.get("id"),
                "citation": citation,
                "style": "IEEE"
            })
        
        return {
            "id": f"citations_{abs(hash(str(papers))) % 10000}",
            "style": "IEEE",
            "total_citations": len(citations),
            "citations": citations,
            "bibliography": "\n".join([c["citation"] for c in citations]),
            "created_at": "2024-10-03T10:00:00Z"
        }

    def _get_mock_sample_paper(self, query: str, papers: List[Dict]) -> Dict[str, Any]:
        """Fallback mock sample research paper."""
        return {
            "id": f"paper_{abs(hash(query)) % 10000}",
            "title": f"Advances in {query.title()}: A Comprehensive Review and Future Directions",
            "abstract": f"This paper presents a comprehensive analysis of current developments in {query}. Through systematic review of recent literature and methodological advances, we identify key trends and propose future research directions. Our analysis reveals significant progress in both theoretical understanding and practical applications.",
            "sections": {
                "introduction": {
                    "title": "1. Introduction",
                    "content": f"The field of {query} has experienced rapid growth in recent years, driven by technological advances and increased research interest. This paper aims to provide a comprehensive overview of current state-of-the-art approaches and identify promising directions for future research."
                },
                "literature_review": {
                    "title": "2. Literature Review", 
                    "content": f"Recent studies in {query} have demonstrated significant advances in both methodology and applications. This section reviews key contributions from leading researchers and identifies emerging trends in the field.",
                    "subsections": [
                        {"title": "2.1 Theoretical Foundations", "content": "Fundamental principles and theoretical frameworks..."},
                        {"title": "2.2 Methodological Approaches", "content": "Current methodologies and their comparative advantages..."},
                        {"title": "2.3 Applications and Case Studies", "content": "Real-world applications and validation studies..."}
                    ]
                },
                "methodology": {
                    "title": "3. Methodology",
                    "content": "This study employs a systematic review methodology to analyze current literature and identify key trends. Our approach includes comprehensive database searches, quality assessment, and thematic analysis of findings."
                },
                "results": {
                    "title": "4. Results and Discussion",
                    "content": "Our analysis reveals several key findings regarding the current state and future directions of research in this field. The results demonstrate significant progress while highlighting areas requiring further investigation."
                },
                "conclusion": {
                    "title": "5. Conclusion",
                    "content": f"This comprehensive review of {query} research demonstrates substantial progress in the field while identifying opportunities for future development. Key recommendations include enhanced methodological rigor, increased interdisciplinary collaboration, and focus on practical applications."
                }
            },
            "references_count": len(papers),
            "word_count": 3500,
            "created_at": "2024-10-03T10:00:00Z"
        }

    def _get_mock_interactive_mindmap(self, query: str, papers: List[Dict]) -> Dict[str, Any]:
        """Fallback mock interactive mindmap."""
        # Extract authors and concepts from papers
        authors = set()
        concepts = set([query.lower(), "research", "methodology", "analysis"])
        
        for paper in papers[:5]:
            authors.update(paper.get("authors", [])[:2])
            concepts.update(paper.get("keywords", [])[:3])
        
        nodes = [{"id": "central", "label": query.title(), "type": "central", "x": 400, "y": 300}]
        connections = []
        node_id = 1
        
        # Add concept nodes
        for i, concept in enumerate(list(concepts)[:6]):
            angle = (i / 6) * 2 * 3.14159
            x = 400 + 150 * (1 + 0.3 * i) * (1 if i % 2 == 0 else -1) * abs(angle) / 3.14159
            y = 300 + 150 * (1 + 0.2 * i) * (1 if angle < 3.14159 else -1)
            
            nodes.append({
                "id": f"concept_{node_id}",
                "label": concept.title(),
                "type": "concept", 
                "x": x,
                "y": y,
                "description": f"Key concept related to {query}"
            })
            connections.append({"from": "central", "to": f"concept_{node_id}", "type": "relates_to"})
            node_id += 1
        
        # Add author nodes
        for i, author in enumerate(list(authors)[:4]):
            angle = (i / 4) * 2 * 3.14159 + 0.785  # Offset from concepts
            x = 400 + 120 * (1 if i % 2 == 0 else -1)
            y = 300 + 120 * (1 if i < 2 else -1)
            
            nodes.append({
                "id": f"author_{node_id}",
                "label": author,
                "type": "author",
                "x": x, 
                "y": y,
                "description": f"Researcher in {query}"
            })
            connections.append({"from": "central", "to": f"author_{node_id}", "type": "authored_by"})
            node_id += 1
        
        return {
            "id": f"mindmap_{abs(hash(query)) % 10000}",
            "title": f"Interactive Mind Map: {query.title()}",
            "topic": query,
            "nodes": nodes,
            "connections": connections,
            "node_types": {
                "central": {"color": "#8B5CF6", "size": "large"},
                "concept": {"color": "#06D6A0", "size": "medium"}, 
                "author": {"color": "#F72585", "size": "medium"},
                "paper": {"color": "#FFD60A", "size": "small"}
            },
            "interaction_features": {
                "zoom": True,
                "drag": True, 
                "click_details": True,
                "search": True,
                "filter": True
            },
            "created_at": "2024-10-03T10:00:00Z"
        }

    def _get_mock_mindmap(self, topic: str) -> Dict[str, Any]:
        """Fallback mock mindmap."""
        return {
            "id": f"mm_{abs(hash(topic)) % 10000}",
            "topic": topic,
            "nodes": [
                {"id": 1, "label": topic.title(), "x": 400, "y": 300, "type": "central"},
                {"id": 2, "label": "Methodology", "x": 300, "y": 200, "type": "concept"},
                {"id": 3, "label": "Applications", "x": 500, "y": 200, "type": "concept"},
                {"id": 4, "label": "Future Work", "x": 300, "y": 400, "type": "concept"},
                {"id": 5, "label": "Related Research", "x": 500, "y": 400, "type": "concept"}
            ],
            "connections": [
                {"from": 1, "to": 2},
                {"from": 1, "to": 3},
                {"from": 1, "to": 4},
                {"from": 1, "to": 5}
            ]
        }

# Global MCP client instance
mcp_client = MCPClient()
