# Python APT-like progress bar
## Built on top of: https://github.com/pollev/python_progress_bar and https://github.com/pollev/bash_progress_bar
## Inspired by: wanting to print things while seeing a bar
___
## How To:
* init(), params:
    * ColorTransition (bool)
    * isMoving (bool)
    * spinnerType (int, 0-7)
        * | /  — \
        * ← ↖ ↑ ↗ → ↘ ↓ ↙
        * ▁▂▃▄▅▆▇█▇▆▅▄▃▁
        * ▉▊▋▌▍▎▏▎▍▌▋▊▉
        * ◢ ◣ ◤ ◥
        * ◐ ◓ ◑ ◒
        * ▙ ▛ ▜ ▟ 
        * ◰ ◱ ◲ ◳

* draw_progress_bar(), params:
    * percentage (int)
    * context (string) -> displays maximum 10 characters
    * delay (float)
* destroy() (DONT FORGET)

## Dependencies
* curses
* signal
* time
* colored

## Demo
![Alt text](./preview.gif?raw=true "a little preview")