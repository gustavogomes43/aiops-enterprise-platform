import pytest
from datetime import datetime
# Importando dos novos nomes de pacotes com underscore
from aiops.correlation_engine.event_correlator import CorrelationEngine, Event, EventType, EventSeverity
from aiops.ml_models.anomaly_detector import AnomalyDetector

def test_correlation_logic():
    # Inicializa o motor (usando localhost para teste local)
    engine = CorrelationEngine(redis_host='localhost')
    
    event1 = Event(
        id="1", 
        timestamp=datetime.now(), 
        type=EventType.NETWORK_LATENCY, 
        severity=EventSeverity.CRITICAL, 
        source="router-01", 
        message="High latency detected"
    )
    
    # Adiciona evento e verifica se a lógica de correlação responde
    engine.add_event(event1)
    assert len(engine.events) == 1

def test_anomaly_detection():
    detector = AnomalyDetector()
    # Simula dados de métricas (ex: CPU usage)
    data = [10, 12, 11, 13, 100, 12, 11] 
    anomalies = detector.detect(data)
    
    # O valor 100 deve ser detectado como anomalia
    assert 100 in anomalies