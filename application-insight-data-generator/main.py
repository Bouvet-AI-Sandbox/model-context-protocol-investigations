import argparse
import random
import time
import os
from dotenv import load_dotenv
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
from datetime import datetime

# Load environment variables
load_dotenv()
INSTRUMENTATION_KEY = os.getenv("APPLICATION_INSIGHT_INSTRUMENTATION_KEY")

# Set up OpenCensus Tracer
tracer = Tracer(exporter=AzureExporter(connection_string=f"InstrumentationKey={INSTRUMENTATION_KEY}"),
                 sampler=ProbabilitySampler(1.0))

def send_request_data(method, url, status_code, duration):
    with tracer.span(name="SyntheticRequest") as span:
        span.add_attribute("http.method", method)
        span.add_attribute("http.url", url)
        span.add_attribute("http.status_code", status_code)
        span.add_attribute("http.duration", duration)
        
        print(f"Sent request data: Method={method}, URL={url}, Status={status_code}, Duration={duration}ms")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and send synthetic request data to Application Insights.")
    parser.add_argument("--method", type=str, default="GET", help="HTTP method (GET, POST, etc.)")
    parser.add_argument("--url", type=str, default="https://example.com", help="Request URL")
    parser.add_argument("--status", type=int, default=200, help="HTTP response status code")
    parser.add_argument("--duration", type=int, default=random.randint(50, 500), help="Request duration in ms")
    
    args = parser.parse_args()
    
    send_request_data(args.method, args.url, args.status, args.duration)
