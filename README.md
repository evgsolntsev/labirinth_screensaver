# labirinth_screensaver
Small Python module for xscreensaver.

It uses pygame and xlib, so if you want to run it, you need `pip3 install pygame xlib`.

To make your xscreensaver use this, add the following string to your `.xscreensaver`:
* `"labirinth" 	/path/to/repo/wrap.sh \n\`

Then call `xscreensaver-demo` as always and choose "labirinth" here.
