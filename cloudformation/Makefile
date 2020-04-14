API_STACK_NAME	:= MozDefSlackTriageBotAPI
USER_STACK_NAME	:= MozDefSlackTriageBotUser
CODE_STORAGE_S3_PREFIX	:= mozdef-slack-triage-bot-api
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
PROD_SLACK_CLIENT_ID	:= 2258538036.890553022979
DEV_SLACK_CLIENT_ID		:= 371351187216.856548004901
# PROD_SLACK_CLIENT_SECRET	:= Get this value here : https://api.slack.com/apps/AS6G90NUT/general
# DEV_SLACK_CLIENT_SECRET		:= Get this value here : https://api.slack.com/apps/AR6G404SH/general

.PHONE: deploy-mozdef-slack-triage-bot-user
deploy-mozdef-slack-triage-bot-user:
	aws cloudformation deploy --template-file slack-triage-bot-user.yaml --stack-name $(USER_STACK_NAME) \
        --capabilities CAPABILITY_IAM

.PHONE: deploy-mozdef-slack-triage-bot-api-dev
deploy-mozdef-slack-triage-bot-api-dev:
	@test -n "$(DEV_SLACK_CLIENT_SECRET)"
	./deploy.sh \
		 $(DEV_ACCOUNT_ID) \
		 slack-triage-bot-api.yaml \
		 $(DEV_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME) \
		 $(API_STACK_NAME) \
		 $(CODE_STORAGE_S3_PREFIX) \
		 "CustomDomainName=$(DEV_DOMAIN_NAME) \
		 	DomainNameZone=$(DEV_DOMAIN_ZONE) \
		 	CertificateArn=$(DEV_CERT_ARN) \
			SlackClientId=$(DEV_SLACK_CLIENT_ID) \
			SlackClientSecret=$(DEV_SLACK_CLIENT_SECRET)" \
		 SlackTriageBotApiUrl

.PHONE: deploy-mozdef-slack-triage-bot-api
deploy-mozdef-slack-triage-bot-api:
	@test -n "$(PROD_SLACK_CLIENT_SECRET)"
	./deploy.sh \
		 $(PROD_ACCOUNT_ID) \
		 slack-triage-bot-api.yaml \
		 $(PROD_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME) \
		 $(API_STACK_NAME) \
		 $(CODE_STORAGE_S3_PREFIX) \
		 "CustomDomainName=$(PROD_DOMAIN_NAME) \
		 	DomainNameZone=$(PROD_DOMAIN_ZONE) \
		 	CertificateArn=$(PROD_CERT_ARN) \
			SlackClientId=$(PROD_SLACK_CLIENT_ID) \
			SlackClientSecret=$(PROD_SLACK_CLIENT_SECRET)" \
		 SlackTriageBotApiUrl

.PHONE: test-mozdef-slack-triage-bot-api-http
test-mozdef-slack-triage-bot-api-http:
	URL="`aws cloudformation describe-stacks --stack-name $(API_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotApiUrl'].OutputValue" --output text`test" && \
	curl $$URL

.PHONE: test-mozdef-slack-triage-bot-api-invoke
test-mozdef-slack-triage-bot-api-invoke:
	FUNCTION_NAME=`aws cloudformation describe-stacks --stack-name $(API_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotFunctionName'].OutputValue" --output text` && \
	ACCESS_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerAccessKeyId'].OutputValue" --output text` && \
	SECRET_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerSecretAccessKey'].OutputValue" --output text` && \
	AWS_ACCESS_KEY_ID=$$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$$SECRET_KEY AWS_SESSION_TOKEN= aws lambda invoke \
	  --function-name $$FUNCTION_NAME \
	  --payload '{"identifier": "9Zo02m4B7gIfixq3c4Xh", "alert": "duo_bypass_codes_generated", "identityConfidence": "highest", "summary": "DUO bypass codes have been generated for your account. ", "user": "$(EMAIL_ADDRESS)"}' \
	  response.json && \
	cat response.json && \
	rm response.json

.PHONE: test-mozdef-slack-triage-bot-api-invoke-ssh1
test-mozdef-slack-triage-bot-api-invoke-ssh1:
	FUNCTION_NAME=`aws cloudformation describe-stacks --stack-name $(API_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotFunctionName'].OutputValue" --output text` && \
	ACCESS_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerAccessKeyId'].OutputValue" --output text` && \
	SECRET_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerSecretAccessKey'].OutputValue" --output text` && \
	AWS_ACCESS_KEY_ID=$$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$$SECRET_KEY AWS_SESSION_TOKEN= aws lambda invoke \
	  --function-name $$FUNCTION_NAME \
	  --payload '{"identifier": "9Zo02m4B7gIfixq3c4Xh", "alert": "sensitive_host_session", "identityConfidence": "low", "summary": "An SSH session to a potentially sensitive host sensitive.example.com was made by your user account.", "user": "$(EMAIL_ADDRESS)"}' \
	  response.json && \
	cat response.json && \
	rm response.json

.PHONE: test-mozdef-slack-triage-bot-api-invoke-ssh2
test-mozdef-slack-triage-bot-api-invoke-ssh2:
	FUNCTION_NAME=`aws cloudformation describe-stacks --stack-name $(API_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotFunctionName'].OutputValue" --output text` && \
	ACCESS_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerAccessKeyId'].OutputValue" --output text` && \
	SECRET_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerSecretAccessKey'].OutputValue" --output text` && \
	AWS_ACCESS_KEY_ID=$$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$$SECRET_KEY AWS_SESSION_TOKEN= aws lambda invoke \
	  --function-name $$FUNCTION_NAME \
	  --payload '{"identifier": "9Zo02m4B7gIfixq3c4Xh", "alert": "ssh_access_sign_releng", "identityConfidence": "low", "summary": "An SSH session was established to host host.example.com by your user account.", "user": "$(EMAIL_ADDRESS)"}' \
	  response.json && \
	cat response.json && \
	rm response.json

.PHONE: test-mozdef-slack-triage-bot-api-invoke-duo-code-used
test-mozdef-slack-triage-bot-api-invoke-duo-code-used:
	FUNCTION_NAME=`aws cloudformation describe-stacks --stack-name $(API_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotFunctionName'].OutputValue" --output text` && \
	ACCESS_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerAccessKeyId'].OutputValue" --output text` && \
	SECRET_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerSecretAccessKey'].OutputValue" --output text` && \
	AWS_ACCESS_KEY_ID=$$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$$SECRET_KEY AWS_SESSION_TOKEN= aws lambda invoke \
	  --function-name $$FUNCTION_NAME \
	  --payload '{"identifier": "9Zo02m4B7gIfixq3c4Xh", "alert": "duo_bypass_codes_used", "identityConfidence": "highest", "summary": "DUO bypass codes belonging to your account have been used to ", "user": "$(EMAIL_ADDRESS)"}' \
	  response.json && \
	cat response.json && \
	rm response.json

.PHONE: show-user-credentials
show-user-credentials:
	aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerAccessKeyId'].OutputValue" --output text && \
	aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerSecretAccessKey'].OutputValue" --output text

.PHONE: discover-lambda-function-name
discover-lambda-function-name:
	ACCESS_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerAccessKeyId'].OutputValue" --output text` && \
	SECRET_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerSecretAccessKey'].OutputValue" --output text` && \
	AWS_ACCESS_KEY_ID=$$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$$SECRET_KEY AWS_SESSION_TOKEN= aws lambda list-functions \
	  --query "Functions[?contains(FunctionName, '-SlackTriageBotApiFunction-')].FunctionName" --output text

.PHONE: discover-sqs-queue-url
discover-sqs-queue-url:
	FUNCTION_NAME=`aws cloudformation describe-stacks --stack-name $(API_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotFunctionName'].OutputValue" --output text` && \
	ACCESS_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerAccessKeyId'].OutputValue" --output text` && \
	SECRET_KEY=`aws cloudformation describe-stacks --stack-name $(USER_STACK_NAME) --query "Stacks[0].Outputs[?OutputKey=='SlackTriageBotInvokerSecretAccessKey'].OutputValue" --output text` && \
	AWS_ACCESS_KEY_ID=$$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$$SECRET_KEY AWS_SESSION_TOKEN= aws lambda invoke \
	  --function-name $$FUNCTION_NAME \
	  --payload '{"action": "discover-sqs-queue-url"}' \
		--output json \
	  response.json && \
	cat response.json && \
	rm response.json


# TODO : Deal with the fact that this API isn't "deployed" when you first create the CloudFormation stack
# options : https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-deployment.html
# https://docs.aws.amazon.com/cli/latest/reference/apigateway/create-deployment.html
# web UI
# http://www.awslessons.com/2017/aws-api-gateway-missing-authentication-token/
