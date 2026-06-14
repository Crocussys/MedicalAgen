"""
REST API РґР»СЏ РјРµРґРёС†РёРЅСЃРєРѕРіРѕ Р°РіРµРЅС‚Р°
REST API Module
"""

from typing import Optional
import json

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from loguru import logger

from core.agent import MedicalAgent
from config import settings


# РњРѕРґРµР»Рё Р·Р°РїСЂРѕСЃР°/РѕС‚РІРµС‚Р°
class PatientMessageRequest(BaseModel):
    """Р—Р°РїСЂРѕСЃ СЃРѕРѕР±С‰РµРЅРёСЏ РѕС‚ РїР°С†РёРµРЅС‚Р°"""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None


class DoctorMessageRequest(BaseModel):
    """Р—Р°РїСЂРѕСЃ СЃРѕРѕР±С‰РµРЅРёСЏ РѕС‚ РІСЂР°С‡Р°"""
    message: str = Field(..., min_length=1, max_length=1000)
    command: Optional[str] = None


class MessageResponse(BaseModel):
    """РћС‚РІРµС‚ Р°РіРµРЅС‚Р°"""
    response: str
    session_id: str
    timestamp: str


class SessionInfoResponse(BaseModel):
    """РРЅС„РѕСЂРјР°С†РёСЏ Рѕ СЃРµР°РЅСЃРµ"""
    session_id: str
    patient_info: dict
    symptoms_count: int
    conversation_length: int


def create_app(agent: MedicalAgent) -> FastAPI:
    """РЎРѕР·РґР°С‚СЊ FastAPI РїСЂРёР»РѕР¶РµРЅРёРµ"""
    
    app = FastAPI(
        title="Medical AI Assistant",
        description="REST API РґР»СЏ РјРµРґРёС†РёРЅСЃРєРѕРіРѕ РР-РїРѕРјРѕС‰РЅРёРєР°",
        version="1.0.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # РњР°СЂС€СЂСѓС‚С‹
    
    @app.get("/health")
    async def health():
        """РџСЂРѕРІРµСЂРєР° Р·РґРѕСЂРѕРІСЊСЏ РїСЂРёР»РѕР¶РµРЅРёСЏ"""
        return {"status": "ok", "agent_initialized": agent.initialized}
    
    @app.get("/session")
    async def get_session():
        """РџРѕР»СѓС‡РёС‚СЊ РёРЅС„РѕСЂРјР°С†РёСЋ Рѕ С‚РµРєСѓС‰РµРј СЃРµР°РЅСЃРµ"""
        info = agent.get_session_info()
        return SessionInfoResponse(**info)
    
    @app.post("/message/patient")
    async def process_patient_message(request: PatientMessageRequest):
        """РћР±СЂР°Р±РѕС‚Р°С‚СЊ СЃРѕРѕР±С‰РµРЅРёРµ РїР°С†РёРµРЅС‚Р°"""
        try:
            response = await agent.process_patient_message(request.message)
            return MessageResponse(
                response=response,
                session_id=agent.current_session["id"],
                timestamp=agent.current_session["id"]
            )
        except Exception as e:
            logger.error(f"Error processing patient message: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/message/doctor")
    async def process_doctor_message(request: DoctorMessageRequest):
        """РћР±СЂР°Р±РѕС‚Р°С‚СЊ СЃРѕРѕР±С‰РµРЅРёРµ РІСЂР°С‡Р°"""
        try:
            response = await agent.process_doctor_message(request.message)
            return MessageResponse(
                response=response,
                session_id=agent.current_session["id"],
                timestamp=agent.current_session["id"]
            )
        except Exception as e:
            logger.error(f"Error processing doctor message: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/session/reset")
    async def reset_session():
        """РЎР±СЂРѕСЃРёС‚СЊ СЃРµР°РЅСЃ"""
        agent.reset_session()
        return {"status": "reset"}
    
    @app.get("/session/history")
    async def get_history(limit: int = 20):
        """РџРѕР»СѓС‡РёС‚СЊ РёСЃС‚РѕСЂРёСЋ СЂР°Р·РіРѕРІРѕСЂР°"""
        all_messages = agent.memory.get_full_conversation()
        return {"messages": all_messages[-limit:]}
    
    @app.websocket("/ws/chat")
    async def websocket_chat(websocket: WebSocket):
        """WebSocket РґР»СЏ СЂРµР°Р»СЊРЅРѕРіРѕ РІСЂРµРјРµРЅРё С‡Р°С‚Р°"""
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_json()
                role = data.get("role", "patient")
                message = data.get("message", "")
                
                if not message:
                    await websocket.send_json({"error": "Empty message"})
                    continue
                
                # РћР±СЂР°Р±Р°С‚С‹РІР°РµРј СЃРѕРѕР±С‰РµРЅРёРµ
                if role == "patient":
                    response = await agent.process_patient_message(message)
                else:
                    response = await agent.process_doctor_message(message)
                
                # РћС‚РїСЂР°РІР»СЏРµРј РѕС‚РІРµС‚
                await websocket.send_json({
                    "response": response,
                    "session_id": agent.current_session["id"],
                    "role": role
                })
        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket.close(code=1000)
    
    return app


def start_api_server(agent: MedicalAgent, host: str = "0.0.0.0", port: int = 8000):
    """Р—Р°РїСѓСЃС‚РёС‚СЊ REST API СЃРµСЂРІРµСЂ"""
    app = create_app(agent)
    
    logger.info(f"рџљЂ Р—Р°РїСѓСЃРє API СЃРµСЂРІРµСЂР° РЅР° {host}:{port}")
    print(f"""
    в•”в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•—
    в•‘   API Documentation                   в•‘
    в•‘   http://{host}:{port}/docs          в•‘
    в•‘   http://{host}:{port}/redoc          в•‘
    в•љв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ќ
    """)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

