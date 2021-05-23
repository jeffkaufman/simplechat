# SimpleChat

Minimal Slack client that allows someone to participate in an
individual room from the command line.

## Configuration

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
    "users": {
      "U1234": "friendly name here"
    }
  },
  "simplechat": {
    "token": "generate a token shared between client and server",
  }
}

```
