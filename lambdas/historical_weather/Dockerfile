FROM public.ecr.aws/lambda/python:3.12

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements and install Python dependencies
COPY requirements.lock .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.lock

# Copy handler from lambdas/historical_weather/
COPY lambdas/historical_weather/handler.py ${LAMBDA_TASK_ROOT}/

# Set handler
CMD [ "handler.lambda_handler" ]

