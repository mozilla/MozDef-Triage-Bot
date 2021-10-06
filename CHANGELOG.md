# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

* Diagrams and flow descriptions to the README [#26](https://github.com/mozilla/MozDef-Triage-Bot/pull/26) [#27](https://github.com/mozilla/MozDef-Triage-Bot/pull/27)

## [1.2.0] - 2020-04-20

### Changed

* Makefile by adding check for missing client_secrets [#18](https://github.com/mozilla/MozDef-Triage-Bot/pull/18)
* Deployment scripts to support deploying from MacOS [#20](https://github.com/mozilla/MozDef-Triage-Bot/pull/20)

### Fixed

* store_oauth_token ValidationException error [#21](https://github.com/mozilla/MozDef-Triage-Bot/pull/21)
* typo in IAM permission for SSM [#22](https://github.com/mozilla/MozDef-Triage-Bot/pull/22) [#24](https://github.com/mozilla/MozDef-Triage-Bot/pull/24)

## [1.1.0] - 2020-01-02

### Changed

* Exception handling [#9](https://github.com/mozilla/MozDef-Triage-Bot/pull/9) [#10](https://github.com/mozilla/MozDef-Triage-Bot/pull/10)
  * Deal with exceptions differently depending on if the function was called
    by API Gateway or through direct invocation.
  * Pass SlackExceptions through to the invoker of the function.
* IAM user creation, moving it into its own CloudFormation stack [#11](https://github.com/mozilla/MozDef-Triage-Bot/pull/11)
  * This will make the IAM user and API keys durable across API
    stack rebuilds.
    This also grants the IAM user rights to invoke all deployments
    of the API and all SQS queues used by the API
* The result structure one more time to be a JSON dictionary [#11](https://github.com/mozilla/MozDef-Triage-Bot/pull/11)
  * This was changed in 5d0ba05 and then in 74f8d5f
    This is another attempt at getting it right

### Added

* Add support for emitting slackName to MozDef
  * This emits an additional piece of information to MozDef about
    the user, the user's Slack username in the slackName field of
    the SQS message

## [1.0.0] - 2019-12-27

Big update to the bot [#5](https://github.com/mozilla/MozDef-Triage-Bot/pull/5)

### Added

* Functions to utils
    * store_oauth_token : Store an OAuth 2 access token in SSM parameter store
    * get_access_token : Fetch the OAuth 2 access token for a given client_id from cache or SSM
      parameter store
    * emit_to_mozdef : Send a message with the user's response to SQS for pickup by MozDef
    * call_slack : POST to a slack URL and return the result
    * provision_token : Given an OAuth 2 code, obtain a Slack access token and store it
    * redirect_to_slack_authorize : Build a Slack OAuth 2 authorization URL and redirect the user to it
* Functions to app
    * API calls
        * process_api_call : Process an API Gateway call depending on the URL path called
            * `/authorize` : utils.redirect_to_slack_authorize
            * `/redirect_uri` : utils.provision_token
            * `/slack/interactive-endpoint` : handle_message_interaction : Process a user's interaction with a Slack message
                * send_slack_message_response : Respond to a user's selection by updating the Slack message with a reply
    * Direct invocations
        * send_message_to_slack : Send a message to a user via IM or Slack App conversation
            * get_user_from_email : Fetch a slack user dictionary for an email address
            * compose_message : Create a Slack message object
            * create_slack_channel : Create an IM channel with a user
            * post_message : Post a message to a slack channel
* Details on discovering the SQS URL to the README
* Additional test invocations to the Makefile
* SQS URL discovery to the Makefile
* `requests` to the requirements.txt
* New settings to config.py
* A function invoker IAM user with access keys for MozDef to use
  Add working end to end bot [#2](https://github.com/mozilla/MozDef-Triage-Bot/pull/2)

### Changed

* lambda_handler in app to cover all URL paths and direct invocations
* README configuration details
* CloudFormation template to
    * accept Slack client ID and secret
    * Grant Lambda function rights to
        * read and write to SSM parameter store
        * decrypt parameter store secrets
        * send messages to the SQS queue
    * Create the SQS queue
    * Grant the MozDef user rights to read from the SQS queue
    
## [0.9.0] - 2019-11-26

### Added

- The initial slack bot code [#1](https://github.com/mozilla/MozDef-Triage-Bot/pull/1)

## [0.1.0] - 2019-11-01

### Added

- The initial design ideas and specifications for the slack bot

[unreleased]: https://github.com/mozilla/MozDef-Triage-Bot/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/mozilla/MozDef-Triage-Bot/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/mozilla/MozDef-Triage-Bot/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/mozilla/MozDef-Triage-Bot/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/mozilla/MozDef-Triage-Bot/compare/v0.1.0...v0.9.0
[0.1.0]: https://github.com/mozilla/MozDef-Triage-Bot/releases/tag/v0.1.0
