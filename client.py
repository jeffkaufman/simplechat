import time
import curses
import curses.ascii
import json
import urllib.request
import textwrap

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

  def record_sent(self, message):
    self.messages.append(message)
    self.update_main()

def send_message(hook, message):
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

def start(stdscr):
  with open("secrets.json") as inf:
    secrets = json.loads(inf.read())
    hook = secrets["slack"]["hook"]

  display = setup(stdscr)
  while True:
    ch = stdscr.getch()
    if ch == curses.ERR:
      time.sleep(0.01)
      continue

    output = display.handle_ch(ch)
    if output:
      send_message(hook, output)
      display.record_sent(output)

if __name__ == "__main__":
  stdscr = curses.initscr()
  try:
    start(stdscr)
  finally:
    cleanup(stdscr)
