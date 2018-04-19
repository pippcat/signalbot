# Signalbot

Signalbot is a Python script which can send Signal messages via Email and/or SMS (using www.clockworksms.com API). It's relying on signal-cli (https://github.com/AsamK/signal-cli) to fetch the actual messages. Configuration is done in by renaming config_default.ini to config.ini and modifying it.

## Warning

This script is only tested on a Raspberry Pi 2 running Raspbian Jessie, Python 2.7.9 and signal_cli 0.5.6. Your results may vary. Feel free to try and help me improve it.

## CLI arguments

You may pass the following arguments to signalbot.py to overwrite defaults set in config.ini:

- `--mail` override config and send mail
- `--notmail` override config and do not send mail
- `--sms` override config and send SMS
- `--notsms` override config and do not send SMS
- `--response` override config and send email responses to group
- `--notresponse` override config and do not send email responses to group
- `--fetch` override config and fetch new signal messages
- `--notfetch` override config and do not fetch new signal messages
- `--debug` override config and switch on debug mode
- `--notdebug` override config and switch off debug mode
- `--emptydb` override config and delete message database after processing
- `--notemptydb` override config and keep message database after processing

## Known issues

- SMS module doesn't check for length of messages
- Mail informing non Signal user about new messages from other non Signal users doesn't support attachments yet
- users are untrusted if they reinstall signal and therefore messages don't come through. As a workaround you can manually trust the new key using signal cli: `signal-cli -u yourNumber trust -a untrustedNumber`

## ToDos

- add possibility to choose between multiple groups to be forwarded to different recipients
- reworking sendmail() function to support a list of attachments
- support more MIMEtypes in getmail()
- check message length and split into multiple sms if necessary
- add filter which removes cited part of email response to group
- add archive function to bot

## Changelog

- 0.6.1 - email responses from non signal users will be sent by mail to other non signal users too
- 0.6   - bot now checks for email responses and sends them to signal group
- 0.5.2 - code clean up
- 0.5.1 - added timestamp to mail header
- 0.5   - fixed unicode fuckup
- 0.4   - included check for maximum attachment size
- 0.3   - included contact names
- 0.2   - now with config.ini
- 0.1   - first quick and dirty implementation
