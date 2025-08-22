import datetime
import numpy as np
from collections import deque
from sklearn.ensemble import IsolationForest


import logging

class AdvancedAnomalyDetector:
    def __init__(self, threshold=10, time_window=60, train_interval=30, max_samples=1000, alert_callback=None, log_file="./logs/anomaly_log.txt"):
        self.threshold = threshold
        self.time_window = time_window
        self.event_queue = deque()
        self.samples = deque(maxlen=max_samples)
        self.train_interval = train_interval
        self.last_trained = datetime.datetime.now()
        self.model = None
        self.alert_callback = alert_callback
        self.log_file = log_file
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

    def _train_model(self):
        if len(self.samples) < self.threshold * 2:
            return
        feature_matrix = np.array(self.samples)
        self.model = IsolationForest(contamination=float(self.threshold) / len(self.samples))
        self.model.fit(feature_matrix)
        logging.info("Isolation Forest model retrained with %d samples.", len(self.samples))

    def add_event(self, feature_vector):
        current_time = datetime.datetime.now()
        self.event_queue.append((current_time, feature_vector))
        self.samples.append(feature_vector)

        # Remove old events outside the time window
        while self.event_queue and (current_time - self.event_queue[0][0]).seconds > self.time_window:
            self.event_queue.popleft()

        # Retrain model if needed
        if (current_time - self.last_trained).seconds > self.train_interval:
            self._train_model()
            self.last_trained = current_time

        # Anomaly detection
        if self.model is not None:
            prediction = self.model.predict([feature_vector])
            if prediction[0] == -1:
                msg = f"Anomaly detected: unusual event pattern! Feature: {feature_vector}"
                print(msg)
                logging.warning(msg)
                if self.alert_callback:
                    self.alert_callback(msg)
                self.event_queue.clear()


