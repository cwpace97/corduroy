aws sns publish `
--topic-arn "arn:aws:sns:us-east-1:717279707480:sns-dynamo-data-topic" `
--message "file://tests/input_data/copper.json"

# aws lambda invoke --function-name loveland-data-v1