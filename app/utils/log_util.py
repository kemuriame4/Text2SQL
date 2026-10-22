from uuid import uuid4

from  loguru import logger

import sys
from loguru import logger
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

def setup_telemetry(service_name: str = "my-fastapi-service"):
    # 1. 配置 OpenTelemetry TracerProvider
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # 2. 配置 Loguru，通过 patcher 注入 trace_id 和 span_id
    logger.remove()
    
    def otel_patcher(record):
        """将 OTel 上下文注入 Loguru 的 record 中。"""
        span = trace.get_current_span()
        if span.is_recording():
            ctx = span.get_span_context()
            record["extra"]["trace_id"] = format(ctx.trace_id, "032x")
            record["extra"]["span_id"] = format(ctx.span_id, "016x")
        else:
            record["extra"]["trace_id"] = uuid4().hex
            record["extra"]["span_id"] = "0000000000000000"

    logger.configure(patcher=otel_patcher)

    # 3. 配置日志输出格式，加入 trace_id
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<magenta>trace_id={extra[trace_id]}</magenta> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    logger.add(sys.stdout, format=log_format, level="INFO", colorize=True)


if __name__ == "__main__":
    setup_telemetry()
    logger.error("Invalid order ID")
    logger.info("Successfully fetched order")
    logger.debug("Successfully fetched order")