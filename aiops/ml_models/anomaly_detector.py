from statistics import mean, stdev


class AnomalyDetector:
    def __init__(self, threshold=2):
        self.threshold = threshold

    def detect(self, data):
        """
        Detecta anomalias usando desvio padrão
        """
        if len(data) < 2:
            return []

        avg = mean(data)
        deviation = stdev(data)

        anomalies = []

        for value in data:
            if abs(value - avg) > self.threshold * deviation:
                anomalies.append(value)

        return anomalies