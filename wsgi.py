import sys
import traceback
import json

def ok(msg="ok"):
  return "200 OK", [("Content-Type", "text/plain")], msg

def handle_request(environ, start_response):
  content_length = int(environ.get('CONTENT_LENGTH', 0))
  post_raw = environ['wsgi.input'].read(content_length)
  post_json = json.loads(post_raw)
  msgtype = post_json["type"]

  with open("/tmp/slack.txt", "w") as outf:
    outf.write(json.dumps(post_json))

  if msgtype == "url_verification":
    return ok(post_json["challenge"])
  elif msgtype == "event_callback" and post_json["event"]["type"] == "message":
    text = post_json["event"]["text"]
    # todo: send this to simplechat. long poll?
    return ok()

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
