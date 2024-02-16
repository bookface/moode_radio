# moode_radio
PC Interface to Moode Audio in python using PySide6 and an mpc executable.

This is a program to run on your PC and communicate with Moode Audio running on a Rasperry PI.
It requires PySide6 and an mpc executable (I installed mine via Cygwin on Windows, apt on Linux).
If you download a backup from Moode, you can place the "station_data.json" file into this
directory.  It will allow you to display a list of stations and play the url.  The
five radio buttons on the radio image will allow you to run your favorites.  For now, 
the station names/urls are coded in main.py.  I will probably move this to an ini file.

1. Right or left mouse drags, left mouse selects if it's over a defined field.
2. Press the volume knob to change the Volume, but easier to just use the scroll wheel
   when over the knob.
3. Press the tuning knob to toggle play/pause.
4. Press one of the radio buttons to play your favorite stations.
5. Press the tuning display to select a station.
6. Press the badge to bring up a web browser.  There is a python based brower here
   but you can run your own.  Again, see the top of the main.py file.
7. The default size of the application is the size of the radio image. It
   can be scaled via the scale ('scale' in the moode_system.ini) parameter
   to BorderLessWindow.
8. If the directory 'radio-logos' exists (also from the Moode backup), the logo of
   the station selected via the tuner will be displayed
   