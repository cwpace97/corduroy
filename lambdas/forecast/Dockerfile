FROM public.ecr.aws/lambda/python:3.12

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements and install Python dependencies
COPY requirements.lock .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.lock

# Copy handler from lambdas/forecast/
COPY lambdas/forecast/handler.py ${LAMBDA_TASK_ROOT}/

# Copy weather directory
COPY weather/ ./weather/

# Set handler
CMD [ "handler.lambda_handler" ]

