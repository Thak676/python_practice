
Only tested in wsl.

It is named 'l01' simply because it is the first iteration of this library, and there are probably more to come.

IMPORT:

I import it using uv. After doing uv init:

uv add --editable PATH_TO_LIB

# Example 1, blue sky:

```
import pygame
from l01 import *
from pygame.locals import *

init(640, 640)

while True:
        fill_screen(19, 214, 248)
        for event in pygame.event.get():
                if event.type == QUIT:
                        quit()
        update_screen()
```

# Example 2, blue sky with cloud:
(you must supply your own image)

```
import pygame
from l01 import *
from pygame.locals import *

init(640, 640)
cloud = Image_Rect("images/clouds/cloud_1.png", 100, 100)

while True:
        fill_screen(14, 218, 248)
        cloud.draw()
        for event in pygame.event.get():
                if event.type == QUIT:
                        quit()
        update_screen()
```
