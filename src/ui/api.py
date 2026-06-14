"""
REST API для медицинского агента
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


# Модели запроса/ответа
class PatientMessageRequest(BaseModel):
    """Запрос сообщения от пациента"""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None


class DoctorMessageRequest(BaseModel):
    """Запрос сообщения от врача"""
    message: str = Field(..., min_length=1, max_length=1000)
    command: Optional[str] = None


class MessageResponse(BaseModel):
    """Ответ агента"""
    response: str
    session_id: str
    timestamp: str


class SessionInfoResponse(BaseModel):
    """Информация о сеансе"""
    session_id: str
    patient_info: dict
    symptoms_count: int
    conversation_length: int


def create_app(agent: MedicalAgent) -> FastAPI:
    """Создать FastAPI приложение"""
    
    app = FastAPI(
        title="Medical AI Assistant",
        description="REST API для медицинского ИИ-помощника",
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
    
    # Маршруты
    
    @app.get("/health")
    async def health():
        """Проверка здоровья приложения"""
        return {"status": "ok", "agent_initialized": agent.initialized}
    
    @app.get("/session")
    async def get_session():
        """Получить информацию о текущем сеансе"""
        info = agent.get_session_info()
        return SessionInfoResponse(**info)
    
    @app.post("/message/patient")
    async def process_patient_message(request: PatientMessageRequest):
        """Обработать сообщение пациента"""
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
        """Обработать сообщение врача"""
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
        """Сбросить сеанс"""
        agent.reset_session()
        return {"status": "reset"}
    
    @app.get("/session/history")
    async def get_history(limit: int = 20):
        """Получить историю разговора"""
        all_messages = agent.memory.get_full_conversation()
        return {"messages": all_messages[-limit:]}
    
    @app.websocket("/ws/chat")
    async def websocket_chat(websocket: WebSocket):
        """WebSocket для реального времени чата"""
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_json()
                role = data.get("role", "patient")
                message = data.get("message", "")
                
                if not message:
                    await websocket.send_json({"error": "Empty message"})
                    continue
                
                # Обрабатываем сообщение
                if role == "patient":
                    response = await agent.process_patient_message(message)
                else:
                    response = await agent.process_doctor_message(message)
                
                # Отправляем ответ
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
    """Запустить REST API сервер"""
    app = create_app(agent)
    
    logger.info(f"🚀 Запуск API сервера на {host}:{port}")
    print(f"""
    ╔═══════════════════════════════════════╗
    ║   API Documentation                   ║
    ║   http://{host}:{port}/docs          ║
    ║   http://{host}:{port}/redoc          ║
    ╚═══════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

