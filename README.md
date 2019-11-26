# MozDef-Triage-Bot
A Slack bot that facilitates triaging MozDef alerts by automating outreach to Mozillians

## slack-triage-bot-api

### Deployment

To deploy the slack-triage-bot-api into AWS run

```shell script
make deploy-mozdef-slack-triage-bot-api
```

or

```shell script
make deploy-mozdef-slack-triage-bot-api-dev
```

depending on the account

### Testing

You can test invoking the function with

```shell script
make test-mozdef-slack-triage-bot-api-invoke
```

which will pass

```json
{"foo": "baz"}
```

to the API which will return

```json
{"result": "bar"}
```

You can also test the API Gateway interface by running

```shell script
make test-mozdef-slack-triage-bot-api-http
```

which will hit the `/test` API endpoint and get back a 200 `API request received`

You can also visit the `/error` endpoint to get a 400 or any other endpoint to get a 404