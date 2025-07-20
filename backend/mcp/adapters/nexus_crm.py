"""
Nexus CRM MCP Adapter

Provides MCP interface for Nexus CRM system.
This adapter translates MCP requests into Nexus CRM API calls.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp

from mcp.schemas import ToolDefinition
from mcp.config import ToolConfig
from core.logging_config import get_logger

logger = get_logger(__name__)


class NexusCRMAdapter:
    """
    MCP Adapter for Nexus CRM
    
    Provides access to:
    - Contact management
    - Deal tracking
    - Activity logging
    - Sales analytics
    """
    
    def __init__(self, endpoint: str = "http://localhost:8002"):
        self.endpoint = endpoint.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """Get all tool definitions provided by Nexus CRM"""
        return [
            ToolDefinition(
                name="nexus_crm.manage_contacts",
                description="Create, read, update, or delete contacts in the CRM",
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "read", "update", "delete", "list", "search"],
                            "description": "Action to perform"
                        },
                        "contact_id": {
                            "type": "string",
                            "description": "Contact ID (required for read, update, delete)"
                        },
                        "data": {
                            "type": "object",
                            "description": "Contact data for create/update",
                            "properties": {
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                                "phone": {"type": "string"},
                                "company": {"type": "string"},
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "custom_fields": {"type": "object"}
                            }
                        },
                        "filters": {
                            "type": "object",
                            "description": "Filters for list/search actions",
                            "properties": {
                                "status": {"type": "string", "enum": ["active", "inactive", "all"]},
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "created_after": {"type": "string", "format": "date"},
                                "limit": {"type": "integer", "minimum": 1, "maximum": 100}
                            }
                        }
                    },
                    "required": ["action"]
                },
                examples=[
                    {
                        "input": {
                            "action": "create",
                            "data": {
                                "name": "John Smith",
                                "email": "john@example.com",
                                "tags": ["premium", "fitness"]
                            }
                        },
                        "output": {
                            "contact_id": "cnt_123456",
                            "created": True
                        }
                    }
                ]
            ),
            
            ToolDefinition(
                name="nexus_crm.manage_deals",
                description="Track and manage sales deals/opportunities",
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "read", "update", "close", "list"],
                            "description": "Action to perform"
                        },
                        "deal_id": {
                            "type": "string",
                            "description": "Deal ID (required for read, update, close)"
                        },
                        "data": {
                            "type": "object",
                            "description": "Deal data",
                            "properties": {
                                "title": {"type": "string"},
                                "contact_id": {"type": "string"},
                                "value": {"type": "number"},
                                "stage": {
                                    "type": "string",
                                    "enum": ["lead", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"]
                                },
                                "probability": {"type": "number", "minimum": 0, "maximum": 100},
                                "expected_close": {"type": "string", "format": "date"}
                            }
                        },
                        "outcome": {
                            "type": "string",
                            "enum": ["won", "lost"],
                            "description": "Outcome when closing a deal"
                        }
                    },
                    "required": ["action"]
                }
            ),
            
            ToolDefinition(
                name="nexus_crm.log_activity",
                description="Log activities, calls, meetings, and interactions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "activity_type": {
                            "type": "string",
                            "enum": ["call", "email", "meeting", "note", "task"],
                            "description": "Type of activity"
                        },
                        "contact_id": {
                            "type": "string",
                            "description": "Associated contact ID"
                        },
                        "deal_id": {
                            "type": "string",
                            "description": "Associated deal ID (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Activity description or notes"
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Duration for calls/meetings"
                        },
                        "outcome": {
                            "type": "string",
                            "description": "Activity outcome"
                        },
                        "follow_up_date": {
                            "type": "string",
                            "format": "date",
                            "description": "Date for follow-up task"
                        }
                    },
                    "required": ["activity_type", "description"]
                }
            ),
            
            ToolDefinition(
                name="nexus_crm.get_analytics",
                description="Get CRM analytics and sales metrics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "metric": {
                            "type": "string",
                            "enum": ["pipeline", "conversion", "activity", "revenue", "forecast"],
                            "description": "Type of analytics to retrieve"
                        },
                        "period": {
                            "type": "string",
                            "enum": ["today", "week", "month", "quarter", "year"],
                            "description": "Time period for analytics"
                        },
                        "group_by": {
                            "type": "string",
                            "enum": ["agent", "stage", "source", "product"],
                            "description": "Group results by dimension"
                        }
                    },
                    "required": ["metric"]
                }
            ),
            
            ToolDefinition(
                name="nexus_crm.sync_with_genesis",
                description="Sync CRM data with GENESIS AI insights",
                input_schema={
                    "type": "object",
                    "properties": {
                        "sync_type": {
                            "type": "string",
                            "enum": ["contacts_to_genesis", "insights_to_crm", "bidirectional"],
                            "description": "Direction of synchronization"
                        },
                        "data_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["engagement_scores", "ai_recommendations", "conversation_history", "training_progress"]
                            },
                            "description": "Types of data to sync"
                        },
                        "contact_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific contacts to sync (optional)"
                        }
                    },
                    "required": ["sync_type", "data_types"]
                }
            )
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self.session:
            await self.initialize()
        
        # Route to appropriate handler
        handlers = {
            "nexus_crm.manage_contacts": self._manage_contacts,
            "nexus_crm.manage_deals": self._manage_deals,
            "nexus_crm.log_activity": self._log_activity,
            "nexus_crm.get_analytics": self._get_analytics,
            "nexus_crm.sync_with_genesis": self._sync_with_genesis
        }
        
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            return await handler(arguments)
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            return {"error": str(e)}
    
    async def _manage_contacts(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage contacts in the CRM"""
        action = args["action"]
        
        if action == "create":
            # Simulated contact creation
            data = args.get("data", {})
            return {
                "contact_id": f"cnt_{datetime.utcnow().timestamp()}",
                "created": True,
                "data": data
            }
        
        elif action == "list":
            # Simulated contact listing
            filters = args.get("filters", {})
            limit = filters.get("limit", 10)
            
            contacts = []
            for i in range(min(limit, 5)):  # Return max 5 simulated contacts
                contacts.append({
                    "contact_id": f"cnt_00{i+1}",
                    "name": f"Client {i+1}",
                    "email": f"client{i+1}@example.com",
                    "status": "active",
                    "tags": ["fitness", "premium"] if i % 2 == 0 else ["fitness"],
                    "created_at": (datetime.utcnow() - timedelta(days=i*7)).isoformat()
                })
            
            return {
                "contacts": contacts,
                "total": 156,
                "page": 1,
                "has_more": True
            }
        
        elif action == "read":
            contact_id = args.get("contact_id")
            if not contact_id:
                return {"error": "contact_id required for read action"}
            
            return {
                "contact_id": contact_id,
                "name": "John Smith",
                "email": "john@example.com",
                "phone": "+1-555-0123",
                "company": "FitLife Inc",
                "tags": ["premium", "fitness", "nutrition"],
                "engagement_score": 85,
                "last_activity": datetime.utcnow().isoformat(),
                "lifetime_value": 4250.00
            }
        
        return {"error": f"Action {action} not implemented in simulation"}
    
    async def _manage_deals(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage sales deals"""
        action = args["action"]
        
        if action == "create":
            data = args.get("data", {})
            return {
                "deal_id": f"deal_{datetime.utcnow().timestamp()}",
                "created": True,
                "data": data,
                "stage": data.get("stage", "lead")
            }
        
        elif action == "list":
            # Simulated deal pipeline
            return {
                "deals": [
                    {
                        "deal_id": "deal_001",
                        "title": "Premium AI Coaching Package",
                        "contact_id": "cnt_001",
                        "value": 2500.00,
                        "stage": "proposal",
                        "probability": 75,
                        "expected_close": (datetime.utcnow() + timedelta(days=14)).isoformat()
                    },
                    {
                        "deal_id": "deal_002",
                        "title": "Corporate Wellness Program",
                        "contact_id": "cnt_045",
                        "value": 15000.00,
                        "stage": "negotiation",
                        "probability": 60,
                        "expected_close": (datetime.utcnow() + timedelta(days=30)).isoformat()
                    }
                ],
                "total_value": 87500.00,
                "weighted_value": 52500.00
            }
        
        return {"error": f"Action {action} not implemented in simulation"}
    
    async def _log_activity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Log CRM activity"""
        activity_type = args["activity_type"]
        description = args["description"]
        
        activity_id = f"act_{datetime.utcnow().timestamp()}"
        
        return {
            "activity_id": activity_id,
            "type": activity_type,
            "logged_at": datetime.utcnow().isoformat(),
            "description": description,
            "logged_by": "GENESIS AI Integration"
        }
    
    async def _get_analytics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get CRM analytics"""
        metric = args["metric"]
        period = args.get("period", "month")
        
        analytics = {
            "metric": metric,
            "period": period,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        if metric == "pipeline":
            analytics["data"] = {
                "stages": {
                    "lead": {"count": 45, "value": 112500.00},
                    "qualified": {"count": 28, "value": 84000.00},
                    "proposal": {"count": 12, "value": 48000.00},
                    "negotiation": {"count": 8, "value": 32000.00},
                    "closed_won": {"count": 23, "value": 57500.00}
                },
                "total_open_value": 276500.00,
                "weighted_value": 165900.00
            }
        
        elif metric == "conversion":
            analytics["data"] = {
                "lead_to_qualified": 0.62,
                "qualified_to_proposal": 0.43,
                "proposal_to_close": 0.75,
                "overall": 0.20,
                "average_deal_size": 2500.00,
                "average_sales_cycle_days": 21
            }
        
        elif metric == "activity":
            analytics["data"] = {
                "total_activities": 847,
                "by_type": {
                    "call": 234,
                    "email": 389,
                    "meeting": 124,
                    "note": 100
                },
                "average_per_contact": 5.4,
                "most_active_day": "Tuesday"
            }
        
        elif metric == "revenue":
            analytics["data"] = {
                "closed_won": 57500.00,
                "average_deal": 2500.00,
                "by_product": {
                    "AI Coaching": 32500.00,
                    "Nutrition Plans": 15000.00,
                    "Corporate Programs": 10000.00
                },
                "growth_rate": 0.15
            }
        
        elif metric == "forecast":
            analytics["data"] = {
                "current_month": 45000.00,
                "next_month": 52000.00,
                "quarter": 147000.00,
                "confidence": 0.78,
                "best_case": 165000.00,
                "worst_case": 125000.00
            }
        
        return analytics
    
    async def _sync_with_genesis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data between CRM and GENESIS"""
        sync_type = args["sync_type"]
        data_types = args["data_types"]
        contact_ids = args.get("contact_ids", [])
        
        sync_result = {
            "sync_id": f"sync_{datetime.utcnow().timestamp()}",
            "type": sync_type,
            "started_at": datetime.utcnow().isoformat(),
            "data_types": data_types
        }
        
        if sync_type in ["contacts_to_genesis", "bidirectional"]:
            # Simulate syncing contacts to GENESIS
            sync_result["contacts_synced"] = len(contact_ids) if contact_ids else 156
            sync_result["genesis_updated"] = True
        
        if sync_type in ["insights_to_crm", "bidirectional"]:
            # Simulate syncing insights to CRM
            sync_result["insights_synced"] = {
                "engagement_scores": 142,
                "ai_recommendations": 89,
                "conversation_summaries": 234
            }
            sync_result["crm_updated"] = True
        
        sync_result["completed_at"] = datetime.utcnow().isoformat()
        sync_result["status"] = "success"
        
        return sync_result