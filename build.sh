cd .\lambdas\
copy .\rds_lambda.py .\python_libs\
cd .\python_libs\
7z a -r ..\build_zips\rds_lambda.zip *
cd ..
aws s3 cp build_zips\rds_lambda.zip s3://cwpace97-lambda-deployments/rds-lambda/

cd ..
serverless deploy