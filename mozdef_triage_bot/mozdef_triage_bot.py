import os
import slack


def main():
    client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])

    response = client.chat_postMessage(
        channel='#mozdef-alert-triaging',
        text='Hello world!')


if __name__ == '__main__':
    main()
