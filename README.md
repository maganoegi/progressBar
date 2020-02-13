# Python APT-like progress bar
## Built on top of: https://github.com/pollev/python_progress_bar and https://github.com/pollev/bash_progress_bar
## Inspired by: wanting to print things while seeing a bar
___
## How To:
* init(), params:
    * ColorTransition (bool) (optional) 
    * isMoving (bool) (optional)
    * spinnerType (int, 0-5) (optional)
        * 0) | /  — \
        * 1) ←↖↑↗→↘↓↙
        * 2) ▁▂▃▄▅▆▇█▇▆▅▄▃▁
        * 3) ▉▊▋▌▍▎▏▎▍▌▋▊▉
        * 4) ◢◣◤◥
        * 5) ◐◓◑◒

* draw_progress_bar(), params:
    * percentage (int)
    * delay (float) (optional)
* destroy() (DONT FORGET)

## Dependencies
* curses
* signal
* random
* string
* time
* colored