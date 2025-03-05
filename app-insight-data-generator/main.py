import time
import random
import requests
import logging
import os
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.trace import SpanKind, StatusCode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
CONNECTION_STRING = os.getenv("APPLICATION_INSIGHT_CONNECTION_STRING")

logger.info(f"CONNECTION_STRING={CONNECTION_STRING}")
# Configure Azure Monitor
configure_azure_monitor(
    connection_string=CONNECTION_STRING,
    enable_live_metrics=False
)

# enable_live_metrics=True causes recursion exception on 1.6.5 ref https://github.com/Azure/azure-sdk-for-python/issues/39914

tracer = trace.get_tracer(__name__)

# Instrument requests
RequestsInstrumentor().instrument()

# Test web request generator
def generate_web_request():
    urls = ["https://example.com/login", "https://example.com/api/data", "https://example.com/products"]
    statuses = [200, 201, 400, 404, 500]
    
    url = random.choice(urls)
    status = random.choice(statuses)
    response_time = round(random.uniform(0.1, 5.0), 2)  # Simulate response times

    with tracer.start_as_current_span("simulated_request", kind=SpanKind.SERVER) as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.url", url)
        span.set_attribute("http.status_code", status)
        span.set_attribute("duration", response_time*1000)
        span.set_attribute("User.AuthenticatedUserId", "kjarisk")

        if status == 500:
            try:
                raise ValueError("Simulated error for logging to Application Insights exceptions table")
            except Exception as e:
                    span.record_exception(e)
        elif status == 400: 
            logger.info(f"Bad request from user likely due to outdated client software.")
        

        logger.info(f"Request to {url} | Status: {status} | Response Time: {response_time}s")

    time.sleep(response_time)

# Function to deliberately generate and log an exception for testing
def generate_exception():
    try:
        raise ValueError("Simulated error for logging to Application Insights exceptions table")
    except Exception as e:
        logger.error("Caught exception in generate_exception", exc_info=True)
        with tracer.start_as_current_span("logged_exception", kind=SpanKind.INTERNAL) as span:
            span.record_exception(e)
            span.set_status(StatusCode.ERROR)

# Run test data generation loop
if __name__ == "__main__":
    logger.info("Starting test web request generator...")
    

    for _ in range(20):  # Generate 10 test requests
        generate_web_request()