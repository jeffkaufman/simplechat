# SimpleChat

Minimal Slack client that allows someone to participate in an
individual room from the command line.

## Configuration

### Add new app

1. Visit https://api.slack.com/apps
2. Click "Create New App"
3. Click "From an App Manifest"
4. Select a workspace
5. Select "JSON"
6. Paste app manifest (with `Test` changed to the user's name):
 ```
{
    "_metadata": {
        "major_version": 1,
        "minor_version": 1
    },
    "display_information": {
        "name": "Test",
        "description": "SimpleChat for Test",
        "background_color": "#cf0a0a"
    },
    "features": {
        "app_home": {
            "home_tab_enabled": false,
            "messages_tab_enabled": true,
            "messages_tab_read_only_enabled": true
        },
        "bot_user": {
            "display_name": "Test",
            "always_online": false
        }
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "incoming-webhook",
                "channels:history"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "request_url": "https://www.jefftk.com/simplechat?Test",
            "bot_events": [
                "message.channels"
            ]
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "is_hosted": false
    }
}
```
7. Click "Create"
8. Click "Install to Workspace"
9. Give it a channel to post in
10. Make a new file under `secrets/` with the "Verification Token, "like:
   ```
{
  "slack": {
    "token": "the Verification Token from Slack's UI"
  },
  "simplechat": {
    "token": "generate a random string"
  }
}

   ```
11. Also put the simplechat token in the client JSON as simplechat.token
12. Click "Incoming Webhooks" on the left
13. Copy the webhook URL and put it in the client JSON as slack.hook

### Client

#### `secrets-client.json`

```
{
  "slack": {
    "hook": "https://hooks.slack.com/services/TBD",
  },
  "simplechat": {
    "token": "generate a token shared between client and server",
    "url": "your deployment url"
  }
}

```

### Server

#### Nginx

```
location /simplechat {
  include uwsgi_params;
  uwsgi_pass 127.0.0.1:7095;
}
```

#### `/etc/systemd/system/uwsgi-simplechat.service`

```
[Unit]
Description=uWSGI SimpleChat

[Service]
ExecStart=/usr/local/bin/uwsgi --socket :7095 --wsgi-file /home/jefftk/code/simplechat/wsgi.py
Restart=always
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```

Then run:

```
sudo systemctl enable uwsgi-simplechat
sudo service uwsgi-simplechat start
```

#### `secrets-server.json`

```
{
  "slack": {
    "token": "token slack sends on messages, so you can tell it's real",
  },
  "simplechat": {
    "token": "generate a token shared between client and server",
  }
}
```

#### `users.json`

"users": {
  "U1234": "friendly name here"
}
