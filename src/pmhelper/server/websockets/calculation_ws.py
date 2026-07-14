"""
WebSocket handler for real-time calculations.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json
import logging

from ...calculations import calculate_pm_value_async

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(
            f"Client disconnected. Total: {len(self.active_connections)}")

    async def send_message(self, websocket: WebSocket,
                           message: Dict[str, Any]):
        await websocket.send_json(message)


manager = ConnectionManager()


async def handle_calculation_websocket(websocket: WebSocket):
    """
    Handle WebSocket connections for real-time calculations.

    Message format:
    Client -> Server:
    {
        "type": "calculate",
        "data": {
            "value": 42,
            "parameters": {}
        }
    }

    Server -> Client:
    {
        "type": "result",
        "success": true,
        "data": {...}
    }
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "calculate":
                user_data = message.get("data", {})

                try:
                    # Process using core calculation function
                    result = await calculate_pm_value_async(
                        value=user_data.get("value", 0),
                        parameters=user_data.get("parameters", {})
                    )

                    # Send result back
                    await manager.send_message(websocket, {
                        "type": "result",
                        "success": True,
                        "data": {
                            "result": result["result"],
                            "execution_time_ms": result["execution_time_ms"],
                            "metadata": result["metadata"]
                        }
                    })

                except Exception as e:
                    await manager.send_message(websocket, {
                        "type": "error",
                        "success": False,
                        "error": str(e)
                    })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
