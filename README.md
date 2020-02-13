# Python Progress Bar - apt style
#### Built on top of: 
* https://github.com/pollev/python_progress_bar and 
* https://github.com/pollev/bash_progress_bar
#### Inspired by: wanting to print things while seeing a bar
___
## Functions:
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

## Examples:
```python
    # create the bar
    init(color=True, dynamic=False, spinner=7, empty=True)
    
    maxval = 100
    for i in range(maxval):
        # do something... and calculate percentage!
        draw_progress_bar(percentage, "doing something...", delay=0.05)
    destroy() # remove this progress bar, and recreate another if needed!
```

```python
    # create another bar
    init(color=False, dynamic=False, spinner=4, empty=False)
 
    # first action... ~33%
    draw_progress_bar(33, "first step", 0.05)

    # second action... ~67%
    draw_progress_bar(67, "second step", 0.05)

    # ... and final action, ~99%
    draw_progress_bar(99, "this is it...", 0.05)

    destroy() # don't forget to remove this one, too!
```

## Dependencies
* curses
* signal
* time
* colored

## Demo
![Alt text](./preview.gif?raw=true "a little preview")
### Code of above demo example:
```python
def random_string(string_length=30):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


init(color=True, dynamic=False, spinner=7, empty=True)
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
```