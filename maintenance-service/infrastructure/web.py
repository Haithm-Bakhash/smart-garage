import logging
import pika
import json
from fastapi import APIRouter, Header, HTTPException
from domain.models import CarRequest, MaintenanceResponse
from use_cases.analyzer import analyze_car

logger = logging.getLogger(__name__)
router = APIRouter()


def send_notification(car_make, car_model, issues, cost):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='maintenance_alerts')
        
        message = {
            "car": f"{car_make} {car_model}",
            "issues": issues,
            "cost": cost
        }
        
        channel.basic_publish(exchange='', routing_key='maintenance_alerts', body=json.dumps(message))
        connection.close()
        logger.info("Successfully sent background alert to RabbitMQ!")
    except Exception as e:
        logger.error(f"Failed to send RabbitMQ message: {e}")


@router.post("/api/v1/maintenance/predict", response_model=MaintenanceResponse)
def predict_maintenance(request_data: CarRequest, x_api_key: str = Header(default="my-super-secret-password")):
    if x_api_key != "my-super-secret-password":
        logger.warning("Failed login attempt with bad API key!")
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    logger.info(f"Processing AI request for {request_data.make} {request_data.model}")
    
    result = analyze_car(request_data)
    
    send_notification(request_data.make, request_data.model, result.upcoming_issues, result.estimated_cost_usd)
    return result