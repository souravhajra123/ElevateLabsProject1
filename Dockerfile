FROM python:3.9
WORKDIR /app
COPY app.py .
RUN pip install flask prometheus_client jaeger-client opentracing
ENV JAEGER_AGENT_HOST=jaeger
EXPOSE 5000
CMD ["python", "app.py"]
