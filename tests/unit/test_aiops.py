import pytest
from datetime import datetime
# Importando os dois motores da sua plataforma AIOps
from aiops.correlation_engine.event_correlator import CorrelationEngine, Event, EventType, EventSeverity
from aiops.ml_models.anomaly_detector import AnomalyDetector

# Teste 1: Valida a lógica de correlação (Passo 6)
def test_event_correlation_logic():
    engine = CorrelationEngine(redis_host='localhost')
    now = datetime.now()
    
    events = [
        Event(timestamp=now, source="auth-service", event_type=EventType.LOG_ERROR, severity=EventSeverity.CRITICAL, message="DB Timeout"),
        Event(timestamp=now, source="api-gateway", event_type=EventType.TRACE_ERROR, severity=EventSeverity.WARNING, message="504 Gateway Timeout")
    ]
    
    groups = engine.correlate_events(events)
    assert len(groups) >= 1

# Teste 2: Valida a inicialização do Detector de Anomalias (Passo 7)
def test_anomaly_detector_initialization():
    detector = AnomalyDetector(redis_host='localhost')
    assert detector is not None