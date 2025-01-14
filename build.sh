# DOCKER BUILD
docker build -t docker-images:latest . --provenance=false
docker tag docker-images:latest 717279707480.dkr.ecr.us-east-1.amazonaws.com/docker-images:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 717279707480.dkr.ecr.us-east-1.amazonaws.com/docker-images
docker push 717279707480.dkr.ecr.us-east-1.amazonaws.com/docker-images:latest

# LAMBDA BUILD
cd .\lambdas\
copy .\dynamo_lambda.py .\python_libs\
cd .\python_libs\
7z a -r ..\build_zips\dynamo_lambda.zip *
cd ..
aws s3 cp build_zips\dynamo_lambda.zip s3://cwpace97-lambda-deployments/dynamo-lambda/
cd ..

# DEPLOY STACK
serverless deploy