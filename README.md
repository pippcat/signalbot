# Signalbot

Signalbot is a Python script which can send Signal messages via Email and/or SMS (using www.clockworksms.com API). It's relying on signal-cli (https://github.com/AsamK/signal-cli) to fetch the actual messages. Configuration is done in by renaming config_default.ini to config.ini and modifying it.

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
- Messages from other contacts or groups will still be downloaded and then be lost.

## ToDos

- add possibility to choose between multiple groups to be forwarded to different recipients
- check message length and split into multiple sms if necessary

## Changelog

- 0.6   - bot now checks for email responses and sends them to signal group
- 0.5.2 - code clean up
- 0.5.1 - added timestamp to mail header
- 0.5   - fixed unicode fuckup
- 0.4   - included check for maximum attachment size
- 0.3   - included contact names
- 0.2   - now with config.ini
- 0.1   - first quick and dirty implementation
