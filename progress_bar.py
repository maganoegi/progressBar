#!/usr/bin/env python3

# Author Sergey Platonov
# Built on top of: 
#   https://github.com/pollev/python_progress_bar and https://github.com/pollev/bash_progress_bar


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

# Parameters
COLOR_ENABLED = False
DYNAMIC_ENABLED = False

# Variables
CURRENT_SWIRL = 1
TRAPPING_ENABLED = False
TRAP_SET = False
original_sigint_handler = None

def init(color=True, dynamic=False):
    global TRAPPING_ENABLED
    global COLOR_ENABLED
    global DYNAMIC_ENABLED

    TRAPPING_ENABLED = True
    COLOR_ENABLED = color
    DYNAMIC_ENABLED = dynamic

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


def draw_progress_bar(percentage, delay=None):
    lines = curses.tigetnum("lines")
    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)

    # Move cursor position to last row
    __print_control_code("\033[" + str(lines) + ";0f")

    # Clear progress bar
    __tput("el")

    # Draw progress bar
    __print_bar_text(percentage)

    # Restore cursor position
    __print_control_code(CODE_RESTORE_CURSOR)

    if delay: time.sleep(delay)


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
    swirlies = "\|/-—"
    sw = swirlies[CURRENT_SWIRL]
    CURRENT_SWIRL = (CURRENT_SWIRL + 1) % 5
    return sw

def getColor(percentage):
    index = percentage // 10
    return COLORS[index]

def __print_bar_text(percentage):
    cols = curses.tigetnum("cols")
    bar_size = cols - 21 # 17 before

    # Config matching
    color = f"{COLOR_FG}{colored.bg(getColor(percentage)) if COLOR_ENABLED else GREEN}"


    # Prepare progress bar
    complete_size = (bar_size * percentage) / 100
    remainder_size = bar_size - complete_size
    sw = getSwirl()

    progress_bar = \
            f"[{color}{'#' * int(complete_size)}{RESTORE_FG}{RESTORE_BG}{sw * int(remainder_size)}]" if DYNAMIC_ENABLED \
        else f"[{sw}] [{color}{'#' * int(complete_size)}{RESTORE_FG}{RESTORE_BG}{'.' * int(remainder_size)}]"

    # Print progress bar
    __print_control_code(f" Progress {percentage}% {progress_bar}")


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


    init(color=False, dynamic=False)

    percentage = 0
    maxval = 500
    for i in range(maxval):

        percentage = int(float(i)/float(maxval) * 50.0)
        
        generate_some_output_and_sleep()

        draw_progress_bar(percentage, 0.002)
    
    for i in range(maxval):

        percentage2 = percentage + int(float(i)/float(maxval) * 50.0)
        
        generate_some_output_and_sleep()

        draw_progress_bar(percentage2, 0.01)

    destroy()


