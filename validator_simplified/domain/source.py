import requests
import time
import configparser
from typing import Dict, Any, Optional, List
import csv
from datetime import datetime

class Source:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._session = requests.Session()
        self.results: List[Dict[str, float]] = []
    
    @property
    def url(self) -> str:
        return f"{self.host}:{self.port}"
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.url}/{endpoint.lstrip('/')}"
        return self._session.request(method, url, json=data)
    
    def add_result(self, timestamps: Dict[str, float]):
        self.results.append(timestamps)
    
    def save_results(self, filename: str = "results.csv"):
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['T0', 'T1', 'T2', 'T3', 'T4', 'T5'])
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
    
    def __str__(self) -> str:
        return self.url 