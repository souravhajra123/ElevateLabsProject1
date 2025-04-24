from flask import Flask, request
import logging
import time
import random
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from jaeger_client import Config
import opentracing

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    filename='/app/logs/app.log',  # <- This must match your Docker volume!
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Request latency', ['endpoint'])

# Tracing setup
def init_tracer(service):
    config = Config(config={"sampler": {"type": "const", "param": 1}}, service_name=service)
    return config.initialize_tracer()

tracer = init_tracer('flask-app')
opentracing.tracer = tracer

@app.route('/logs')
def hello():
    app.logger.info('Hello route was called')
    return "Hello, logs!"

@app.route('/')
def index():
    with tracer.start_span('index-span') as span:
        start = time.time()
        REQUEST_COUNT.labels(request.method, '/').inc()
        time.sleep(random.random())
        latency = time.time() - start
        REQUEST_LATENCY.labels('/').observe(latency)
        app.logger.info("Home page accessed")
        return "Hello, Monitoring!"

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
