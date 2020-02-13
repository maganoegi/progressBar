#!/usr/bin/env python3

import curses
import signal
import random
import string
import time

# Usage:
# import progress_bar                           <- Import this module
# progress_bar.enable_trapping()                <- optional to clean up properly if user presses ctrl-c
# progress_bar.setup_scroll_area()              <- create empty progress bar
# progress_bar.draw_progress_bar(10)            <- advance progress bar
# progress_bar.draw_progress_bar(40)            <- advance progress bar
# progress_bar.block_progress_bar(45)           <- turns the progress bar yellow to indicate some action is requested from the user
# progress_bar.draw_progress_bar(90)            <- advance progress bar
# progress_bar.destroy_scroll_area()            <- remove progress bar


# Constants
CODE_SAVE_CURSOR = "\033[s"
CODE_RESTORE_CURSOR = "\033[u"
CODE_CURSOR_IN_SCROLL_AREA = "\033[1A"
COLOR_FG = '\033[30m'
GREEN = '\033[42m'
RED = '\033[41m'
YELLOW = '\033[43m'
RESTORE_FG = '\033[39m'
RESTORE_BG = '\033[49m'

CURRENT_SWIRL = 1


# Variables
TRAPPING_ENABLED = False
TRAP_SET = False
original_sigint_handler = None

def setup_scroll_area():
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


def destroy_scroll_area():
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


def __print_bar_text(percentage):
    cols = curses.tigetnum("cols")
    bar_size = cols - 21 # 17 before

    sw = getSwirl()


    COLOR_BG = YELLOW
    if percentage < 33: COLOR_BG = RED
    elif percentage > 66: COLOR_BG = GREEN

    color = f"{COLOR_FG}{COLOR_BG}"

    # Prepare progress bar
    complete_size = (bar_size * percentage) / 100
    remainder_size = bar_size - complete_size
    progress_bar = f"[{color}{'#' * int(complete_size)}{RESTORE_FG}{RESTORE_BG}{sw * int(remainder_size)}]"

    # Print progress bar
    __print_control_code(f" Progress {percentage}% {progress_bar}")


def enable_trapping():
    global TRAPPING_ENABLED
    TRAPPING_ENABLED = True


def __trap_on_interrupt():
    global TRAP_SET
    global original_sigint_handler
    # If this function is called, we setup an interrupt handler to cleanup the progress bar
    TRAP_SET = True
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, __cleanup_on_interrupt)


def __cleanup_on_interrupt(sig, frame):
    destroy_scroll_area()
    raise KeyboardInterrupt


def __tput(cmd, *args):
    print(curses.tparm(curses.tigetstr("el")).decode(), end='')


def __print_control_code(code):
    print(code, end='\r')





if __name__ == '__main__':

    def random_string(string_length=30):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(string_length))

    def generate_some_output_and_sleep():
        # print(random_string(), end="\r")
        print(random_string())


    # Make sure that the progress bar is cleaned up when user presses ctrl+c
    enable_trapping()
    # Create progress bar
    setup_scroll_area()

    maxval= 5000
    for i in range(maxval):

        percentage = int(float(i)/float(maxval) * 100.0)
        
        generate_some_output_and_sleep()
        draw_progress_bar(percentage, 0.001)
    destroy_scroll_area()


