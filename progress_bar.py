#!/usr/bin/env python3

# Author Sergey Platonov
# Built on top of: 
#   https://github.com/pollev/python_progress_bar and https://github.com/pollev/bash_progress_bar

# byzanz-record --duration=9 --delay=2  --x=0 --width=950 --height=550 preview.gif

import curses
import signal
import random
import string
import time
import colored

# Constants
CODE_SAVE_CURSOR = "\033[s"
CODE_RESTORE_CURSOR = "\033[u"
CODE_CURSOR_IN_SCROLL_AREA = "\033[1A"
COLOR_FG = '\033[30m'
GREEN = '\033[42m'
RESTORE_FG = '\033[39m'
RESTORE_BG = '\033[49m'
COLORS = [196, 202, 208, 214, 220, 226, 154, 118, 82, 46]
SPINNERS = [
    "\|/—",
    "←↖↑↗→↘↓↙",
    "▁▂▃▄▅▆▇█▇▆▅▄▃▁",
    "▉▊▋▌▍▎▏▎▍▌▋▊▉",
    "◢◣◤◥",
    "◐◓◑◒",
    "▙▛▜▟",
    "◰◱◲◳"
]

# Parameters
COLOR_ENABLED = False
DYNAMIC_ENABLED = False
EMPTY_BAR = False
SPINNER_TYPE = 0

# Variables
CURRENT_SWIRL = 1
TRAPPING_ENABLED = False
TRAP_SET = False
original_sigint_handler = None

def init(color=True, dynamic=False, spinner=0, empty=False):
    global TRAPPING_ENABLED
    global COLOR_ENABLED
    global DYNAMIC_ENABLED
    global SPINNER_TYPE
    global EMPTY_BAR

    TRAPPING_ENABLED = True
    EMPTY_BAR = empty
    COLOR_ENABLED = color
    DYNAMIC_ENABLED = dynamic
    SPINNER_TYPE = spinner

    # Setup curses support (to get information about the terminal we are running in)
    curses.setupterm()

    # If trapping is enabled, we will want to activate it whenever we setup the scroll area and remove it when we break the scroll area
    if TRAPPING_ENABLED:
        __trap_on_interrupt()

    lines = curses.tigetnum("lines") - 1
    # Scroll down a bit to avoid visual glitch when the screen area shrinks by one row
    __print_control_code("\n")

    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)
    # Set scroll region (this will place the cursor in the top left)
    __print_control_code("\033[0;" + str(lines) + "r")

    # Restore cursor but ensure its inside the scrolling area
    __print_control_code(CODE_RESTORE_CURSOR)
    __print_control_code(CODE_CURSOR_IN_SCROLL_AREA)

    # Start empty progress bar
    draw_progress_bar(0)


def destroy():
    lines = curses.tigetnum("lines")
    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)
    # Set scroll region (this will place the cursor in the top left)
    __print_control_code("\033[0;" + str(lines) + "r")

    # Restore cursor but ensure its inside the scrolling area
    __print_control_code(CODE_RESTORE_CURSOR)
    __print_control_code(CODE_CURSOR_IN_SCROLL_AREA)

    # We are done so clear the scroll bar
    __clear_progress_bar()

    # Scroll down a bit to avoid visual glitch when the screen area grows by one row
    __print_control_code("\n\n")

    # Once the scroll area is cleared, we want to remove any trap previously set.
    if TRAP_SET:
        signal.signal(signal.SIGINT, original_sigint_handler)


def draw_progress_bar(percentage, context="", delay=None):
    lines = curses.tigetnum("lines")
    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)

    # Move cursor position to last row
    __print_control_code("\033[" + str(lines) + ";0f")

    # Clear progress bar
    __tput("el")

    # Draw progress bar
    __print_bar_text(percentage, context)

    # Restore cursor position
    __print_control_code(CODE_RESTORE_CURSOR)

    if delay: time.sleep(delay)


def getPercentage(i, max, maxPercent):
    return int(float(i)/float(max) * float(maxPercent))


def __clear_progress_bar():
    lines = curses.tigetnum("lines")
    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)

    # Move cursor position to last row
    __print_control_code("\033[" + str(lines) + ";0f")

    # clear progress bar
    __tput("el")

    # Restore cursor position
    __print_control_code(CODE_RESTORE_CURSOR)


def getSwirl():
    global CURRENT_SWIRL

    swirlies = SPINNERS[SPINNER_TYPE]
    quantity = len(swirlies)

    sw = (swirlies[CURRENT_SWIRL] + swirlies[(CURRENT_SWIRL+1) % quantity] + swirlies[(CURRENT_SWIRL+2) % quantity]) if SPINNER_TYPE == 2 \
        else swirlies[CURRENT_SWIRL]

    CURRENT_SWIRL = (CURRENT_SWIRL + 1) % quantity
    return sw

def getPercentage(i, max, maxPercent):
    return int(float(i)/float(max) * float(maxPercent))

def getColor(percentage):
    index = percentage // 10
    return COLORS[index]

def formatContext(context):
    length = len(context)
    return context[:10] if length > 9 else (context + (" " * (10 - length)))

def __print_bar_text(percentage, context):
    cols = curses.tigetnum("cols")
    bar_size = cols - 24 # 17 before

    # Config matching
    color = f"{COLOR_FG}{colored.bg(getColor(percentage)) if COLOR_ENABLED else GREEN}"

    # Prepare the progress bar values
    complete_size = (bar_size * percentage) / 100
    remainder_size = bar_size - complete_size
    sw = getSwirl()
    _pre = "#" if not EMPTY_BAR else " "
    _post = (sw if DYNAMIC_ENABLED else ".") if not EMPTY_BAR else " "
    _bracketL, _bracketR = ("[", "]") if SPINNER_TYPE != 7 else ("", "")
    _context = formatContext(context) if len(context) > 0 else "Progress"


    # Prepare progress bar
    progress_bar = f"{_bracketL}{sw}{_bracketR} [{color}{_pre * int(complete_size)}{RESTORE_FG}{RESTORE_BG}{_post * int(remainder_size)}]"

    # Print progress bar
    __print_control_code(f" {_context} {str(percentage).zfill(2)}% {progress_bar}")


def __trap_on_interrupt():
    global TRAP_SET
    global original_sigint_handler
    # If this function is called, we setup an interrupt handler to cleanup the progress bar
    TRAP_SET = True
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, __cleanup_on_interrupt)


def __cleanup_on_interrupt(sig, frame):
    destroy()
    raise KeyboardInterrupt


def __tput(cmd, *args):
    print(curses.tparm(curses.tigetstr("el")).decode(), end='')


def __print_control_code(code):
    print(code, end='\r')





if __name__ == '__main__': # TEST

    def random_string(string_length=30):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(string_length))

    def generate_some_output_and_sleep():
        print(random_string())


    init(color=True, dynamic=True, spinner=0, empty=False)

    maxval = 100
    for i in range(maxval):

        percentage = int(float(i)/float(maxval) * 100.0)
        
        print(random_string(), end="\r")

        draw_progress_bar(percentage, "encrypt", 0.05)

    destroy()

    init(color=False, dynamic=False, spinner=4, empty=False)
    
    for i in range(maxval):

        percentage = int(float(i)/float(maxval) * 100.0)
        
        print(random_string())

        draw_progress_bar(percentage, "decrypt", 0.05)

    destroy()



