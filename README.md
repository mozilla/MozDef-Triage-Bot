# MozDef-Triage-Bot
A Slack bot that facilitates triaging MozDef alerts by automating outreach to Mozillians

## slack-triage-bot-api

### Deployment

To deploy the slack-triage-bot-api into AWS
* create the IAM user that MozDef will use to interact with the Lambda function
  and SQS queue
  `make deploy-mozdef-slack-triage-bot-user`
* determine the Slack Client Secret
* Run the make command for the environment you want

```shell script
DEV_SLACK_CLIENT_SECRET=0123456789abcdef0123456789abcdef make deploy-mozdef-slack-triage-bot-api
```

or

```shell script
DEV_SLACK_CLIENT_SECRET=0123456789abcdef0123456789abcdef make deploy-mozdef-slack-triage-bot-api-dev
```

depending on the account

### Configuring in Slack

* Interactive Components
  * Interactivity
    * Request URL
      * `https://example.com/slack/interactive-endpoint`
  * Select Menus
    * Options Load URL
      * `https://example.com/slack/options-load-endpoint`
* OAuth & Permissions
  * OAuth Tokens & Redirect URLs
    * Redirect URLs
      * `https://example.com/redirect_uri`
  * Scopes
    * Bot Token Scopes
      * `users:read.email` : https://api.slack.com/methods/users.lookupByEmail
      * `users:read` : This is required because of users:read.email
      * `im:write` : https://api.slack.com/methods/conversations.open
      * `chat:write` : https://api.slack.com/methods/chat.postMessage
* Install app

### Testing

You can test invoking the function by passing the email address of the user
you want to send a message to and calling

```shell script
EMAIL_ADDRESS=user@example.com make test-mozdef-slack-triage-bot-api-invoke
```

which will pass

```json
{
    "identifier":"9Zo02m4B7gIfixq3c4Xh",
    "alert":"duo_bypass_codes_generated",
    "identityConfidence":"lowest",
    "summary":"DUO bypass codes have been generated for your account. ",
    "user":"user@example.com"
}
```

to the API which will return the JSON response from Slack of the message that
was sent to the user.

You can also test the API Gateway interface by running

```shell script
make test-mozdef-slack-triage-bot-api-http
```

which will hit the `/test` API endpoint and get back a 200 `API request received`

You can also visit the `/error` endpoint to get a 400 or any other endpoint to get a 404

### Discovering the SQS URL containing user responses

To discover the URL of the SQS queue into which user responses are sent, call

```shell script
make discover-sqs-queue-url 
```

which will return a value like

```json
{"result": "https://sqs.us-west-2.amazonaws.com/012345678901/MozDefSlackTraigeBotAPI-SlackTriageBotMozDefQueue-ABCDEFGHIJKL"}
```

### Discovering the Lambda function name

Call the [lambda:ListFunctions](https://docs.aws.amazon.com/lambda/latest/dg/API_ListFunctions.html)
API and filter the results based on the name. You can see an example of this by
running the make command

```shell script
make discover-lambda-function-name 
```

which will return a value like `MozDefSlackTriageBotAPI-SlackTriageBotApiFunction-1N9KLDX1926F3`

### Fetching User API Keys

You can fetch the User API keys from the CloudFormation outputs

```shell script
make show-user-credentials
```