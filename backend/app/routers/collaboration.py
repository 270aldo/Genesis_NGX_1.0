"""
Collaboration API Router for GENESIS NGX Agents.

This module provides endpoints for managing multi-agent collaborations,
including debates, workshops, podcasts, teaching sessions, and case studies.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Path, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from core.auth import get_current_user
from core.logging_config import get_logger
from app.routers.agents import get_agent, get_agents
from agents.skills.collaboration_skills import (
    CollaborationMode,
    InteractionStyle,
    CollaborationContext,
    CollaborationTurn,
    CollaborationOrchestrator
)

# Configure logger
logger = get_logger(__name__)

# Create router
router = APIRouter(
    prefix="/collaboration",
    tags=["collaboration"],
    responses={401: {"description": "Not authorized"}},
)

# Global orchestrator instance
orchestrator = CollaborationOrchestrator()


# Request/Response Models
class StartCollaborationRequest(BaseModel):
    """Request to start a collaboration session"""
    mode: CollaborationMode
    topic: str
    participants: List[str] = Field(..., description="List of agent IDs")
    config: Optional[Dict[str, Any]] = None
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    

class StartDebateRequest(BaseModel):
    """Request to start a debate"""
    topic: str
    participants: List[Dict[str, Any]] = Field(..., description="List of participants with their stances")
    temperature: float = Field(0.7, ge=0.0, le=1.0)


class WorkshopRequest(BaseModel):
    """Request to start a workshop"""
    deliverable: str
    participants: List[Dict[str, Any]] = Field(..., description="List of participants with their roles")
    deadline: Optional[str] = None


class PodcastRequest(BaseModel):
    """Request to start a podcast"""
    theme: str
    episode_format: str
    co_hosts: List[str] = Field(..., description="List of co-host agent IDs")
    audience_level: str = "general"


class TeachingRequest(BaseModel):
    """Request to start a teaching session"""
    subject: str
    learning_objectives: List[str]
    students: List[str] = Field(..., description="List of student agent IDs")
    teaching_style: str = "interactive"


class CaseStudyRequest(BaseModel):
    """Request to start a case study"""
    case: Dict[str, Any]
    analysis_framework: str
    experts: List[str] = Field(..., description="List of expert agent IDs")
    deliverables: List[str]


class TurnRequest(BaseModel):
    """Request to process a turn"""
    agent_id: str
    content: str
    references_previous: Optional[str] = None
    emotion_tone: Optional[str] = None
    confidence: float = Field(1.0, ge=0.0, le=1.0)


class InterventionRequest(BaseModel):
    """Request to apply director intervention"""
    intervention_type: str
    parameters: Dict[str, Any]


class CollaborationResponse(BaseModel):
    """Response from collaboration operations"""
    session_id: str
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


class SessionStatusResponse(BaseModel):
    """Response for session status"""
    session_id: str
    mode: str
    topic: str
    participants: List[str]
    turn_count: int
    status: str
    start_time: datetime
    next_speaker: Optional[str] = None


@router.post("/session/start", response_model=CollaborationResponse)
async def start_collaboration_session(
    request: StartCollaborationRequest,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start a new collaboration session.
    
    Args:
        request: Collaboration start request
        user_id: Authenticated user ID
        
    Returns:
        Session information
    """
    try:
        # Validate participants exist
        available_agents = get_agents()
        for participant_id in request.participants:
            if participant_id not in available_agents:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Agent {participant_id} not found"
                )
        
        # Convert participant IDs to participant objects
        participants = [
            {"id": pid, "name": available_agents[pid].name}
            for pid in request.participants
        ]
        
        # Start session
        session_id = await orchestrator.start_collaboration(
            mode=request.mode,
            topic=request.topic,
            participants=participants,
            config=request.config
        )
        
        logger.info(f"Started collaboration session {session_id} for user {user_id}")
        
        return CollaborationResponse(
            session_id=session_id,
            status="success",
            message="Collaboration session started successfully",
            data={
                "mode": request.mode.value,
                "topic": request.topic,
                "participants": request.participants
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting collaboration session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting collaboration session: {str(e)}"
        )


@router.post("/debate/start", response_model=CollaborationResponse)
async def start_debate(
    request: StartDebateRequest,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start a debate session between agents.
    
    Args:
        request: Debate request
        user_id: Authenticated user ID
        
    Returns:
        Debate session information
    """
    try:
        # Prepare agents for debate
        debate_configs = {}
        for participant in request.participants:
            agent = get_agent(participant["agent_id"])
            if hasattr(agent, 'enter_debate_mode'):
                config = await agent.enter_debate_mode(
                    topic=request.topic,
                    stance=participant["stance"],
                    partners=request.participants,
                    temperature=request.temperature
                )
                debate_configs[participant["agent_id"]] = config
        
        # Start orchestrated session
        session_id = await orchestrator.start_collaboration(
            mode=CollaborationMode.DEBATE,
            topic=request.topic,
            participants=request.participants,
            config={"temperature": request.temperature, "agent_configs": debate_configs}
        )
        
        logger.info(f"Started debate session {session_id} on topic: {request.topic}")
        
        return CollaborationResponse(
            session_id=session_id,
            status="success",
            message="Debate session started successfully",
            data={"debate_configs": debate_configs}
        )
        
    except Exception as e:
        logger.error(f"Error starting debate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting debate: {str(e)}"
        )


@router.post("/workshop/start", response_model=CollaborationResponse)
async def start_workshop(
    request: WorkshopRequest,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start a workshop collaboration session.
    
    Args:
        request: Workshop request
        user_id: Authenticated user ID
        
    Returns:
        Workshop session information
    """
    try:
        # Prepare agents for workshop
        workshop_configs = {}
        for participant in request.participants:
            agent = get_agent(participant["agent_id"])
            if hasattr(agent, 'collaborate_on_task'):
                config = await agent.collaborate_on_task(
                    deliverable=request.deliverable,
                    role=participant["role"],
                    team=request.participants,
                    deadline=request.deadline
                )
                workshop_configs[participant["agent_id"]] = config
        
        # Start orchestrated session
        session_id = await orchestrator.start_collaboration(
            mode=CollaborationMode.WORKSHOP,
            topic=request.deliverable,
            participants=request.participants,
            config={"deadline": request.deadline, "agent_configs": workshop_configs}
        )
        
        logger.info(f"Started workshop session {session_id} for deliverable: {request.deliverable}")
        
        return CollaborationResponse(
            session_id=session_id,
            status="success",
            message="Workshop session started successfully",
            data={"workshop_configs": workshop_configs}
        )
        
    except Exception as e:
        logger.error(f"Error starting workshop: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting workshop: {str(e)}"
        )


@router.post("/podcast/start", response_model=CollaborationResponse)
async def start_podcast(
    request: PodcastRequest,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start a podcast session.
    
    Args:
        request: Podcast request
        user_id: Authenticated user ID
        
    Returns:
        Podcast session information
    """
    try:
        # Prepare co-hosts for podcast
        podcast_configs = {}
        co_hosts = [{"id": host_id, "name": get_agent(host_id).name} for host_id in request.co_hosts]
        
        for host_id in request.co_hosts:
            agent = get_agent(host_id)
            if hasattr(agent, 'enter_podcast_mode'):
                config = await agent.enter_podcast_mode(
                    theme=request.theme,
                    episode_format=request.episode_format,
                    co_hosts=co_hosts,
                    audience_level=request.audience_level
                )
                podcast_configs[host_id] = config
        
        # Start orchestrated session
        session_id = await orchestrator.start_collaboration(
            mode=CollaborationMode.PODCAST,
            topic=request.theme,
            participants=co_hosts,
            config={"format": request.episode_format, "agent_configs": podcast_configs}
        )
        
        logger.info(f"Started podcast session {session_id} on theme: {request.theme}")
        
        return CollaborationResponse(
            session_id=session_id,
            status="success",
            message="Podcast session started successfully",
            data={"podcast_configs": podcast_configs}
        )
        
    except Exception as e:
        logger.error(f"Error starting podcast: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting podcast: {str(e)}"
        )


@router.post("/teaching/start", response_model=CollaborationResponse)
async def start_teaching_session(
    request: TeachingRequest,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start a teaching session.
    
    Args:
        request: Teaching request
        user_id: Authenticated user ID
        
    Returns:
        Teaching session information
    """
    try:
        # Prepare teacher and students
        all_participants = request.students.copy()
        students = [{"id": student_id, "name": get_agent(student_id).name} for student_id in request.students]
        
        # For teaching, we need at least one teacher agent
        if not all_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one student agent is required for teaching session"
            )
        
        teaching_configs = {}
        for student_id in request.students:
            agent = get_agent(student_id)
            if hasattr(agent, 'teach_concept'):
                config = await agent.teach_concept(
                    subject=request.subject,
                    learning_objectives=request.learning_objectives,
                    students=students,
                    teaching_style=request.teaching_style
                )
                teaching_configs[student_id] = config
        
        # Start orchestrated session
        session_id = await orchestrator.start_collaboration(
            mode=CollaborationMode.TEACHING,
            topic=request.subject,
            participants=students,
            config={"objectives": request.learning_objectives, "agent_configs": teaching_configs}
        )
        
        logger.info(f"Started teaching session {session_id} on subject: {request.subject}")
        
        return CollaborationResponse(
            session_id=session_id,
            status="success",
            message="Teaching session started successfully",
            data={"teaching_configs": teaching_configs}
        )
        
    except Exception as e:
        logger.error(f"Error starting teaching session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting teaching session: {str(e)}"
        )


@router.post("/case-study/start", response_model=CollaborationResponse)
async def start_case_study(
    request: CaseStudyRequest,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start a case study analysis session.
    
    Args:
        request: Case study request
        user_id: Authenticated user ID
        
    Returns:
        Case study session information
    """
    try:
        # Prepare experts for case study
        case_study_configs = {}
        experts = [{"id": expert_id, "name": get_agent(expert_id).name} for expert_id in request.experts]
        
        for expert_id in request.experts:
            agent = get_agent(expert_id)
            if hasattr(agent, 'analyze_case_study'):
                config = await agent.analyze_case_study(
                    case=request.case,
                    analysis_framework=request.analysis_framework,
                    experts=experts,
                    deliverables=request.deliverables
                )
                case_study_configs[expert_id] = config
        
        # Start orchestrated session
        session_id = await orchestrator.start_collaboration(
            mode=CollaborationMode.CASE_STUDY,
            topic=request.case.get('title', 'Case Analysis'),
            participants=experts,
            config={"framework": request.analysis_framework, "agent_configs": case_study_configs}
        )
        
        logger.info(f"Started case study session {session_id}")
        
        return CollaborationResponse(
            session_id=session_id,
            status="success",
            message="Case study session started successfully",
            data={"case_study_configs": case_study_configs}
        )
        
    except Exception as e:
        logger.error(f"Error starting case study: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting case study: {str(e)}"
        )


@router.post("/session/{session_id}/turn", response_model=Dict[str, Any])
async def process_turn(
    session_id: str = Path(..., description="Session ID"),
    request: TurnRequest = ...,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process a turn in a collaboration session.
    
    Args:
        session_id: Session ID
        request: Turn request
        user_id: Authenticated user ID
        
    Returns:
        Updated session state
    """
    try:
        # Create collaboration turn
        turn = CollaborationTurn(
            agent_id=request.agent_id,
            content=request.content,
            timestamp=datetime.now(),
            references_previous=request.references_previous,
            emotion_tone=request.emotion_tone,
            confidence=request.confidence
        )
        
        # Process turn through orchestrator
        result = await orchestrator.process_turn(
            session_id=session_id,
            agent_id=request.agent_id,
            turn_content=turn
        )
        
        logger.info(f"Processed turn for agent {request.agent_id} in session {session_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing turn: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing turn: {str(e)}"
        )


@router.post("/session/{session_id}/intervention")
async def apply_intervention(
    session_id: str = Path(..., description="Session ID"),
    request: InterventionRequest = ...,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Apply director intervention to a session.
    
    Args:
        session_id: Session ID
        request: Intervention request
        user_id: Authenticated user ID
        
    Returns:
        Intervention result
    """
    try:
        # For now, this is a placeholder for director interventions
        # In a full implementation, this would modify session state
        logger.info(f"Applied intervention {request.intervention_type} to session {session_id}")
        
        return {
            "session_id": session_id,
            "intervention_applied": True,
            "type": request.intervention_type,
            "parameters": request.parameters
        }
        
    except Exception as e:
        logger.error(f"Error applying intervention: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error applying intervention: {str(e)}"
        )


@router.get("/session/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str = Path(..., description="Session ID"),
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get status of a collaboration session.
    
    Args:
        session_id: Session ID
        user_id: Authenticated user ID
        
    Returns:
        Session status
    """
    try:
        if session_id not in orchestrator.active_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        session = orchestrator.active_sessions[session_id]
        
        return SessionStatusResponse(
            session_id=session_id,
            mode=session["mode"].value,
            topic=session["topic"],
            participants=[p["id"] for p in session["participants"]],
            turn_count=len(session["turns"]),
            status=session["status"],
            start_time=session["start_time"],
            next_speaker=orchestrator._determine_next_speaker(session)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting session status: {str(e)}"
        )


@router.post("/session/{session_id}/end")
async def end_collaboration_session(
    session_id: str = Path(..., description="Session ID"),
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    End a collaboration session.
    
    Args:
        session_id: Session ID
        user_id: Authenticated user ID
        
    Returns:
        Session summary
    """
    try:
        summary = await orchestrator.end_collaboration(session_id)
        
        logger.info(f"Ended collaboration session {session_id}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ending session: {str(e)}"
        )


@router.get("/sessions")
async def list_active_sessions(
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    List all active collaboration sessions.
    
    Args:
        user_id: Authenticated user ID
        
    Returns:
        List of active sessions
    """
    try:
        sessions = []
        for session_id, session in orchestrator.active_sessions.items():
            sessions.append({
                "session_id": session_id,
                "mode": session["mode"].value,
                "topic": session["topic"],
                "participants": [p["id"] for p in session["participants"]],
                "turn_count": len(session["turns"]),
                "status": session["status"],
                "start_time": session["start_time"]
            })
        
        return {"active_sessions": sessions}
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing sessions: {str(e)}"
        )


@router.websocket("/session/{session_id}/stream")
async def collaboration_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time collaboration streaming.
    
    Args:
        websocket: WebSocket connection
        session_id: Session ID to stream
    """
    await websocket.accept()
    
    try:
        while True:
            # In a full implementation, this would stream real-time updates
            # For now, it's a placeholder that maintains the connection
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket stream: {e}")
        await websocket.close()