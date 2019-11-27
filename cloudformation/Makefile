STACK_NAME	:= MozDefSlackTraigeBotAPI
CODE_STORAGE_S3_PREFIX	:= mozdef-slack-traige-bot-api
PROD_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME	:= public.us-west-2.infosec.mozilla.org
DEV_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME	:= public.us-west-2.security.allizom.org
PROD_ACCOUNT_ID		:= 371522382791
DEV_ACCOUNT_ID		:= 656532927350
PROD_DOMAIN_NAME	:= mozdef-triage-bot.security.mozilla.org
DEV_DOMAIN_NAME		:= mozdef-triage-bot.security.allizom.org
PROD_DOMAIN_ZONE	:= security.mozilla.org.
DEV_DOMAIN_ZONE		:= security.allizom.org.
PROD_CERT_ARN		:= arn:aws:acm:us-west-2:371522382791:certificate/71e3c455-de1f-4a9d-b50e-440624854c48
DEV_CERT_ARN		:= arn:aws:acm:us-west-2:656532927350:certificate/2e59930d-ae8c-43fa-adff-ed3b1a902caa

.PHONE: deploy-mozdef-slack-triage-bot-api-dev
deploy-mozdef-slack-triage-bot-api-dev:
	./deploy.sh \
		 $(DEV_ACCOUNT_ID) \
		 slack-triage-bot-api.yaml \
		 $(DEV_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME) \
		 $(STACK_NAME) \
		 $(CODE_STORAGE_S3_PREFIX) \
		 "CustomDomainName=$(DEV_DOMAIN_NAME) \
		 	DomainNameZone=$(DEV_DOMAIN_ZONE) \
		 	CertificateArn=$(DEV_CERT_ARN)" \
		 SlackTriageBotApiUrl

.PHONE: deploy-mozdef-slack-triage-bot-api
deploy-mozdef-slack-triage-bot-api:
	./deploy.sh \
		 $(PROD_ACCOUNT_ID) \
		 slack-triage-bot-api.yaml \
		 $(PROD_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME) \
		 $(STACK_NAME) \
		 $(CODE_STORAGE_S3_PREFIX) \
		 "CustomDomainName=$(PROD_DOMAIN_NAME) \
		 	DomainNameZone=$(PROD_DOMAIN_ZONE) \
		 	CertificateArn=$(PROD_CERT_ARN)" \
		 SlackTriageBotApiUrl

.PHONE: test-mozdef-slack-triage-bot-api-http
test-mozdef-slack-triage-bot-api-http:
	URL="`aws cloudformation describe-stacks --stack-name $(STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotApiUrl'].OutputValue" --output text`test" && \
	curl $$URL

.PHONE: test-mozdef-slack-triage-bot-api-invoke
test-mozdef-slack-triage-bot-api-invoke:
	FUNCTION_NAME=`aws cloudformation describe-stacks --stack-name $(STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotFunctionName'].OutputValue" --output text` && \
	ACCESS_KEY=`aws cloudformation describe-stacks --stack-name $(STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerAccessKeyId'].OutputValue" --output text` && \
	SECRET_KEY=`aws cloudformation describe-stacks --stack-name $(STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerSecretAccessKey'].OutputValue" --output text` && \
	AWS_ACCESS_KEY_ID=$$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$$SECRET_KEY AWS_SESSION_TOKEN= aws lambda invoke --function-name $$FUNCTION_NAME --payload '{"foo": "baz"}' response.json && \
	cat response.json && \
	rm response.json


# TODO : Deal with the fact that this API isn't "deployed" when you first create the CloudFormation stack
# options : https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-deployment.html
# https://docs.aws.amazon.com/cli/latest/reference/apigateway/create-deployment.html
# web UI
# http://www.awslessons.com/2017/aws-api-gateway-missing-authentication-token/
