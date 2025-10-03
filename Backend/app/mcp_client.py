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

# Global MCP client instance
mcp_client = MCPClient()
