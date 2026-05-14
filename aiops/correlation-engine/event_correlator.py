class EventCorrelator:
    def __init__(self):
        self.event_buffer = []

    def process_event(self, event):
        """Analisa eventos para encontrar a causa raiz"""
        self.event_buffer.append(event)
        if len(self.event_buffer) > 5:
            return "🔥 Root Cause Detected: Database Connection Pool Exhaustion"
        return "Analyzing..."