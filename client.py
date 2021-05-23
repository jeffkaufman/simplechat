import time
import curses
import curses.ascii
import json
import urllib.request
import textwrap
import os

with open(os.path.join(os.path.dirname(__file__), "secrets-client.json")) as inf:
  secrets = json.loads(inf.read())
  hook = secrets["slack"]["hook"]
  simplechat_token = secrets["simplechat"]["token"]
  simplechat_url = secrets["simplechat"]["url"]

class Display:
  def __init__(self, stdscr):
    self.stdscr = stdscr
    self.main_height = curses.LINES-2
    self.divider_row = curses.LINES-2
    self.entry_row = curses.LINES-1
    self.composition = []
    self.cursor_pos = 0
    self.messages = []

    self.stdscr.nodelay(True)
    self.stdscr.insstr(self.divider_row, 0, "-"*(curses.COLS))
    self.fix_cursor()

  def write_line(self, row, message):
    self.stdscr.addstr(row, 0, message)
    self.stdscr.clrtoeol()
    self.fix_cursor()

  def set_entry(self, composition):
    composition = "".join(composition)
    self.cursor_pos = len(composition)
    # trim to screen width
    if len(composition) > curses.COLS-1:
      composition = composition[-(curses.COLS-1):]
      self.cursor_pos = curses.COLS-1
    self.write_line(self.entry_row, composition)

  def fix_cursor(self):
    self.stdscr.move(self.entry_row, self.cursor_pos)
    self.stdscr.refresh()

  def handle_ch(self, ch):
    output = None
    if ch <= 255 and chr(ch).isprintable():
      self.composition.append(chr(ch))
    elif ch in [curses.KEY_BACKSPACE, curses.KEY_DC, curses.ascii.DEL]:
      if self.composition:
        self.composition.pop()
    elif ch == curses.ascii.LF:
      output = "".join(self.composition)
      self.composition = []
    self.set_entry(self.composition)
    return output

  def update_main(self):
    lines = []
    for message in self.messages:
      lines.extend(textwrap.wrap(message, width=curses.COLS))
    if len(lines) > self.main_height:
      lines = lines[-self.main_height:]

    for row, line in enumerate(lines):
      self.write_line(row, line)

  def record_message(self, message):
    self.messages.append(message)
    self.update_main()

  def record_sent(self, message):
    self.record_message(message)

  def record_received(self, messages):
    for message in messages:
      self.record_message(message)

def send_message(message):
  payload = json.dumps({
    "text": message,
  }).encode("utf-8")
  req = urllib.request.Request(hook, data=payload, headers={
    "Content-type": "application/json",
  })
  resp = urllib.request.urlopen(req)

def setup(stdscr):
  curses.noecho()
  curses.cbreak()
  stdscr.keypad(True)

  return Display(stdscr)

def cleanup(stdscr):
  curses.nocbreak()
  stdscr.keypad(False)
  curses.echo()
  curses.endwin()

def poll_server():
  payload = json.dumps({
    "type": "get_messages",
    "token": simplechat_token,
  }).encode("utf-8")
  req = urllib.request.Request(simplechat_url, data=payload, headers={
    "Content-type": "application/json",
  })
  resp = urllib.request.urlopen(req)
  return json.loads(resp.read().decode())


def start(stdscr):
  display = setup(stdscr)
  last_poll = time.time()
  last_active = time.time()

  def should_poll():
    interval = 60*5 # normally poll every 5min
    if time.time() - last_active < 60:
      # active in the last minute; poll every second
      interval = 1
    return time.time() - last_poll > interval

  while True:
    if should_poll():
      messages = poll_server()
      last_poll = time.time()
      if messages:
        display.record_received(messages)

    ch = stdscr.getch()
    if ch == curses.ERR:
      time.sleep(0.01)
      continue

    last_active = time.time()
    output = display.handle_ch(ch)
    if output:
      send_message(output)
      display.record_sent(output)

if __name__ == "__main__":
  stdscr = curses.initscr()
  try:
    start(stdscr)
  finally:
    cleanup(stdscr)
