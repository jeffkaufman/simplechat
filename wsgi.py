import sys
import traceback
import json
import os
from collections import namedtuple

if os.path.dirname(__file__):
  os.chdir(os.path.dirname(__file__))

Client = namedtuple(
  "Client",
  ["name",
   "slack_token",
   "simplechat_token",
   "pending_messages"])

clients_by_slack_token = {}
clients_by_simplechat_token = {}
for client_name in os.listdir("secrets"):
  with open(os.path.join("secrets", client_name))as inf:
    try:
      secrets = json.load(inf)
    except json.decoder.JSONDecodeError as e:
      raise RuntimeError("unable to decode %s" % client_name, e)

    client = Client(
      name=client_name.split(".")[0],
      slack_token=secrets["slack"]["token"],
      simplechat_token=secrets["simplechat"]["token"],
      pending_messages=[])
    clients_by_slack_token[client.slack_token] = client
    clients_by_simplechat_token[client.simplechat_token] = client

def ok(msg="ok"):
  return "200 OK", [("Content-Type", "text/plain")], msg

def get_name(userid):
  with open("users.json") as inf:
    try:
      return json.load(inf).get(userid, userid)
    except json.decoder.JSONDecodeError as e:
      raise RuntimeError("unable to decode users.json", e)

def handle_request(environ, start_response):
  content_length = int(environ.get('CONTENT_LENGTH', 0))
  post_raw = environ['wsgi.input'].read(content_length)
  post_json = json.loads(post_raw)
  msgtype = post_json["type"]

  if msgtype == "url_verification":
    return ok(post_json["challenge"])
  elif (msgtype == "event_callback" and
        post_json["event"]["type"] == "message"):
    with open("/tmp/slack.txt", "w") as outf:
      outf.write(json.dumps(post_json))
      outf.write("\n")

    client = clients_by_slack_token.get(post_json["token"], None)
    if client:
      text = post_json["event"]["text"]
      userid = post_json["event"].get("user", None)
      if not userid:
        userid = post_json["event"]["bot_id"]
      username = get_name(userid)
      for recipient in clients_by_slack_token.values():
        recipient.pending_messages.append("%s: %s" % (username, text))
      return ok()
  elif msgtype == "get_messages":
    client = clients_by_simplechat_token.get(post_json["token"], None)
    if client:
      ret = json.dumps(client.pending_messages)
      client.pending_messages.clear()
      return ok(ret)
  return ok("unknown")

def die500(start_response, e):
    trb = traceback.format_exc().encode("utf-8")
    start_response('500 Internal Server Error', [
        ('Content-Type', 'text/plain'),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Max-Age", "86400"),
    ])
    return trb,

def application(environ, start_response):
  try:
    status, headers, body = handle_request(environ, start_response)
    start_response(status, headers)
    return body.encode('utf-8'),
  except Exception as e:
    print("ERROR:", traceback.format_exc(), file=sys.stderr)
    return die500(start_response, e)

def serve():
  from wsgiref.simple_server import make_server
  make_server(b'',8082,application).serve_forever()

if __name__ == "__main__":
  serve()
