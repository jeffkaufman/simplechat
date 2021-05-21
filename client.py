import time
import curses
import curses.ascii

class Display:
  def __init__(self):
    self.main = curses.newwin(curses.LINES-3, curses.COLS, 0, 0)
    self.divider = curses.newwin(1, curses.COLS, curses.LINES-2, 0)
    self.entry = curses.newwin(1, curses.COLS, curses.LINES-1, 0)
    self.composition = []
    
    self.entry.nodelay(True)
    
    self.divider.addstr("-"*(curses.COLS-1))
    self.main.addstr("hello world");

    self.refresh()

  def refresh(self):
    for win in [self.main, self.divider, self.entry]:
      win.refresh()

  def set_entry(self, composition):
    composition = "".join(composition)
    cursor_pos = len(composition)
    # trim to screen width
    if len(composition) > curses.COLS-1:
      composition = composition[-(curses.COLS-1) : -1]
      cursor_pos = curses.COLS-1
    # pad if too short
    composition = composition.ljust(curses.COLS-1, ' ')
    self.entry.addstr(0, 0, composition)
    self.entry.move(0, cursor_pos)
    self.entry.refresh()

  def handle_ch(self, ch):
    output = None
    if ch <= 255 and chr(ch).isprintable():
      self.composition.append(chr(ch))
    elif ch in [curses.KEY_BACKSPACE, curses.KEY_DC, curses.ascii.DEL]:
      if self.composition:
        self.composition.pop(-1)
    elif ch == curses.ascii.LF:
      output = "".join(self.composition)
      self.composition = []
    self.set_entry(self.composition)
    return output
     
def setup(stdscr):
  curses.noecho()
  curses.cbreak()
  stdscr.keypad(True)

  return Display()

def cleanup(stdscr):
  curses.nocbreak()
  stdscr.keypad(False)
  curses.echo()
  curses.endwin()

def start(stdscr):
  display = setup(stdscr)
  while True:
    ch = display.entry.getch()
    if ch == curses.ERR:
      time.sleep(0.01)
      continue

    output = display.handle_ch(ch)
    if output != None:
      pass
      # add output to display
      # send output on net
      

if __name__ == "__main__":
  stdscr = curses.initscr()
  try:
    start(stdscr)
  finally:
    cleanup(stdscr)
