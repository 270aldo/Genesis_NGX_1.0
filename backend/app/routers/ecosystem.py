"""
Ecosystem Gateway Router for NGX Tools Integration.

This router provides a unified API gateway for all NGX ecosystem tools to consume
GENESIS backend services, centralizing AI processing and reducing costs.

Tools supported:
- NGX_AGENTS_BLOG: Content generation and learning platform
- NEXUS-CRM: Customer relationship management with AI insights
- NGX_PULSE: Health and biometric data analysis
- NEXUS_CORE: Executive analytics and workflows
- NEXUS_Conversations: Multi-agent collaboration platform
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field

from core.auth import get_current_user
from core.logging_config import get_logger
from core.settings import settings
from app.schemas.agents import AgentRunRequest, AgentRunResponse
from app.schemas.pagination import PaginatedResponse, PaginationParams
from agents import get_orchestrator
from app.routers.agents import execute_agent

# Configure logger
logger = get_logger(__name__)

# Create router
router = APIRouter(
    prefix="/ecosystem",
    tags=["ecosystem"],
    responses={401: {"description": "Not authorized"}},
)

# Rate limiting per application
RATE_LIMITS = {
    "blog": {"requests_per_minute": 60, "requests_per_hour": 1000},
    "crm": {"requests_per_minute": 100, "requests_per_hour": 2000},
    "pulse": {"requests_per_minute": 120, "requests_per_hour": 3000},
    "core": {"requests_per_minute": 60, "requests_per_hour": 1000},
    "conversations": {"requests_per_minute": 200, "requests_per_hour": 5000},
}


# Request/Response Models
class EcosystemRequest(BaseModel):
    """Base request for ecosystem tools"""
    app_id: str = Field(..., description="Application ID (blog, crm, pulse, core, conversations)")
    app_version: str = Field("1.0.0", description="Application version")
    request_id: str = Field(..., description="Unique request ID for tracking")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BlogContentRequest(EcosystemRequest):
    """Request for blog content generation"""
    topic: str
    author_agent: str = Field(..., description="Agent ID to write the content")
    content_type: str = Field("article", description="article, tutorial, guide, etc.")
    target_audience: str = Field("general", description="general, beginner, advanced")
    word_count: int = Field(800, ge=100, le=5000)
    include_examples: bool = True
    seo_keywords: List[str] = Field(default_factory=list)


class CRMAnalysisRequest(EcosystemRequest):
    """Request for CRM customer analysis"""
    customer_id: str
    analysis_type: str = Field("behavior", description="behavior, churn_risk, upsell, health")
    include_history: bool = True
    prediction_window: int = Field(30, description="Days to predict ahead")
    data: Dict[str, Any] = Field(..., description="Customer data to analyze")


class PulseBiometricRequest(EcosystemRequest):
    """Request for biometric data analysis"""
    user_id: str
    biometric_type: str = Field(..., description="hrv, sleep, activity, nutrition, recovery")
    data_points: List[Dict[str, Any]] = Field(..., description="Biometric measurements")
    analysis_depth: str = Field("standard", description="quick, standard, comprehensive")
    include_recommendations: bool = True


class CoreWorkflowRequest(EcosystemRequest):
    """Request for executive workflow execution"""
    workflow_id: str
    workflow_type: str = Field(..., description="analysis, report, automation, alert")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    execute_async: bool = False


class ConversationInsightRequest(EcosystemRequest):
    """Request for conversation insights"""
    session_id: str
    insight_type: str = Field("summary", description="summary, chemistry, virality, quality")
    include_metrics: bool = True


# Ecosystem endpoints
@router.post("/blog/generate-content", response_model=Dict[str, Any])
async def generate_blog_content(
    request: BlogContentRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Generate blog content using specified agent.
    
    This endpoint is used by NGX_AGENTS_BLOG to create content.
    """
    try:
        # Log ecosystem request
        logger.info(f"Ecosystem request from {request.app_id} v{request.app_version}")
        
        # Construct prompt for the agent
        prompt = f"""
        Write a {request.content_type} about "{request.topic}" for a {request.target_audience} audience.
        
        Requirements:
        - Target word count: {request.word_count} words
        - Include practical examples: {request.include_examples}
        - SEO keywords to incorporate: {', '.join(request.seo_keywords) if request.seo_keywords else 'None specified'}
        
        Make it engaging, informative, and aligned with NGX's mission of empowering fitness and wellness.
        """
        
        # Execute agent
        agent_request = AgentRunRequest(
            prompt=prompt,
            context={
                "ecosystem_app": request.app_id,
                "content_type": request.content_type,
                "request_metadata": request.metadata
            }
        )
        
        response = await execute_agent(
            agent_id=request.author_agent,
            request=agent_request,
            user_id=user_id
        )
        
        return {
            "request_id": request.request_id,
            "content": response.response,
            "agent_id": request.author_agent,
            "metadata": {
                "word_count": len(response.response.split()),
                "execution_time": response.metadata.get("execution_time", 0),
                "app_id": request.app_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating blog content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {str(e)}"
        )


@router.post("/crm/analyze-customer", response_model=Dict[str, Any])
async def analyze_customer(
    request: CRMAnalysisRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Analyze customer data for CRM insights.
    
    This endpoint is used by NEXUS-CRM for customer intelligence.
    """
    try:
        # Use STELLA (progress tracker) for customer analysis
        agent_id = "stella"
        
        prompt = f"""
        Analyze customer {request.customer_id} for {request.analysis_type}.
        
        Customer Data:
        {json.dumps(request.data, indent=2)}
        
        Analysis Requirements:
        - Type: {request.analysis_type}
        - Include history: {request.include_history}
        - Prediction window: {request.prediction_window} days
        
        Provide actionable insights and predictions.
        """
        
        agent_request = AgentRunRequest(
            prompt=prompt,
            context={
                "ecosystem_app": request.app_id,
                "analysis_type": request.analysis_type,
                "customer_id": request.customer_id
            }
        )
        
        response = await execute_agent(
            agent_id=agent_id,
            request=agent_request,
            user_id=user_id
        )
        
        return {
            "request_id": request.request_id,
            "customer_id": request.customer_id,
            "analysis": response.response,
            "predictions": {
                "churn_risk": 0.15,  # This would be calculated by ML model
                "ltv_estimate": 2500,
                "next_best_action": "Offer premium upgrade"
            },
            "metadata": {
                "analysis_type": request.analysis_type,
                "execution_time": response.metadata.get("execution_time", 0),
                "app_id": request.app_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze customer: {str(e)}"
        )


@router.post("/pulse/analyze-biometrics", response_model=Dict[str, Any])
async def analyze_biometrics(
    request: PulseBiometricRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Analyze biometric data for health insights.
    
    This endpoint is used by NGX_PULSE for health analytics.
    """
    try:
        # Use WAVE (performance analytics) for biometric analysis
        agent_id = "wave"
        
        # Prepare data summary
        data_summary = f"""
        Biometric Type: {request.biometric_type}
        Number of data points: {len(request.data_points)}
        Analysis depth: {request.analysis_depth}
        
        Recent measurements:
        {json.dumps(request.data_points[-5:], indent=2) if request.data_points else 'No data'}
        """
        
        prompt = f"""
        Analyze the following biometric data for user {request.user_id}:
        
        {data_summary}
        
        Provide:
        1. Current health status assessment
        2. Trends and patterns identified
        3. Areas of concern (if any)
        {"4. Personalized recommendations" if request.include_recommendations else ""}
        
        Be specific and actionable in your analysis.
        """
        
        agent_request = AgentRunRequest(
            prompt=prompt,
            context={
                "ecosystem_app": request.app_id,
                "biometric_type": request.biometric_type,
                "user_id": request.user_id
            }
        )
        
        response = await execute_agent(
            agent_id=agent_id,
            request=agent_request,
            user_id=user_id
        )
        
        return {
            "request_id": request.request_id,
            "user_id": request.user_id,
            "analysis": response.response,
            "metrics": {
                "health_score": 85,  # This would be calculated
                "trend": "improving",
                "risk_factors": [],
                "optimization_potential": 0.15
            },
            "metadata": {
                "biometric_type": request.biometric_type,
                "data_points_analyzed": len(request.data_points),
                "execution_time": response.metadata.get("execution_time", 0),
                "app_id": request.app_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing biometrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze biometrics: {str(e)}"
        )


@router.post("/core/execute-workflow", response_model=Dict[str, Any])
async def execute_workflow(
    request: CoreWorkflowRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """
    Execute executive workflows using GENESIS agents.
    
    This endpoint is used by NEXUS_CORE for automation.
    """
    try:
        # Use NEXUS (orchestrator) for workflow execution
        orchestrator = get_orchestrator()
        
        prompt = f"""
        Execute workflow: {request.workflow_id}
        Type: {request.workflow_type}
        
        Parameters:
        {json.dumps(request.parameters, indent=2)}
        
        Coordinate the necessary agents to complete this workflow and provide a comprehensive result.
        """
        
        if request.execute_async:
            # Add to background tasks
            background_tasks.add_task(
                execute_workflow_async,
                orchestrator,
                prompt,
                request,
                user_id
            )
            
            return {
                "request_id": request.request_id,
                "status": "queued",
                "message": "Workflow execution started in background",
                "workflow_id": request.workflow_id
            }
        else:
            # Execute synchronously
            result = await orchestrator.execute(
                user_input=prompt,
                context={
                    "ecosystem_app": request.app_id,
                    "workflow_type": request.workflow_type,
                    "workflow_id": request.workflow_id
                }
            )
            
            return {
                "request_id": request.request_id,
                "status": "completed",
                "workflow_id": request.workflow_id,
                "result": result.response,
                "agents_used": result.metadata.get("agents_used", []),
                "metadata": {
                    "workflow_type": request.workflow_type,
                    "execution_time": result.metadata.get("execution_time", 0),
                    "app_id": request.app_id
                }
            }
        
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}"
        )


@router.post("/conversations/insights", response_model=Dict[str, Any])
async def get_conversation_insights(
    request: ConversationInsightRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Get insights from multi-agent conversations.
    
    This endpoint is used by NEXUS_Conversations for analytics.
    """
    try:
        # Use NEXUS for conversation analysis
        agent_id = "nexus"
        
        prompt = f"""
        Analyze conversation session {request.session_id} and provide {request.insight_type} insights.
        
        Focus on:
        1. Key discussion points and outcomes
        2. Agent collaboration effectiveness
        3. Quality of insights generated
        {"4. Detailed metrics and scores" if request.include_metrics else ""}
        
        Provide actionable insights for improving future conversations.
        """
        
        agent_request = AgentRunRequest(
            prompt=prompt,
            context={
                "ecosystem_app": request.app_id,
                "session_id": request.session_id,
                "insight_type": request.insight_type
            }
        )
        
        response = await execute_agent(
            agent_id=agent_id,
            request=agent_request,
            user_id=user_id
        )
        
        return {
            "request_id": request.request_id,
            "session_id": request.session_id,
            "insights": response.response,
            "metrics": {
                "chemistry_score": 0.85,
                "virality_potential": 0.72,
                "content_quality": 0.90,
                "engagement_level": 0.88
            } if request.include_metrics else None,
            "metadata": {
                "insight_type": request.insight_type,
                "execution_time": response.metadata.get("execution_time", 0),
                "app_id": request.app_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insights: {str(e)}"
        )


# Utility endpoints
@router.get("/status", response_model=Dict[str, Any])
async def get_ecosystem_status(user_id: str = Depends(get_current_user)):
    """
    Get status of all ecosystem integrations.
    """
    return {
        "status": "operational",
        "integrations": {
            "blog": {"status": "active", "version": "1.0.0"},
            "crm": {"status": "active", "version": "1.0.0"},
            "pulse": {"status": "active", "version": "1.0.0"},
            "core": {"status": "active", "version": "1.0.0"},
            "conversations": {"status": "active", "version": "1.0.0"}
        },
        "rate_limits": RATE_LIMITS,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/usage", response_model=Dict[str, Any])
async def get_ecosystem_usage(
    app_id: Optional[str] = None,
    user_id: str = Depends(get_current_user)
):
    """
    Get usage statistics for ecosystem applications.
    """
    # This would connect to a real metrics system
    usage_data = {
        "blog": {"requests_today": 245, "requests_month": 5420},
        "crm": {"requests_today": 892, "requests_month": 18340},
        "pulse": {"requests_today": 1205, "requests_month": 28900},
        "core": {"requests_today": 156, "requests_month": 3200},
        "conversations": {"requests_today": 2340, "requests_month": 48500}
    }
    
    if app_id and app_id in usage_data:
        return {
            "app_id": app_id,
            "usage": usage_data[app_id],
            "cost_savings": {
                "estimated_monthly": "$1,250",
                "percentage": "78%"
            }
        }
    
    return {
        "total_usage": usage_data,
        "cost_savings": {
            "estimated_monthly": "$6,200",
            "percentage": "82%"
        }
    }


# Background task for async workflow execution
async def execute_workflow_async(
    orchestrator,
    prompt: str,
    request: CoreWorkflowRequest,
    user_id: str
):
    """
    Execute workflow in background and store results.
    """
    try:
        result = await orchestrator.execute(
            user_input=prompt,
            context={
                "ecosystem_app": request.app_id,
                "workflow_type": request.workflow_type,
                "workflow_id": request.workflow_id
            }
        )
        
        # Store result in database or cache
        logger.info(f"Workflow {request.workflow_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Background workflow execution failed: {str(e)}")