# moode_radio
PC Interface to Moode Audio in python using PySide6 and an mpc executable.

This is a program to run on your PC and communicate with Moode Audio running on a Rasperry PI.
It requires PySide6 and an mpc executable (I installed mine via Cygwin).
If you download a Backup from Moode, you can place the "station_data.json" file into this
directory.  It will allow you to display a list of stations and play the url.  The
five radio buttons on the radio image will allow you to run your favorites.  For now, 
the station names/urls are coded in main.py.  I will probably move this to an ini file.

1. Press the volume knob to change the Volume
2. Press the tuning knob to toggle play/pause.
3. Press one of the radio buttons to play you favorate stations.
4. Press the tuning display to select a station.
5. Press the "Phillips" badge to bring up a web browser.  There is a python based brower here
   but you can run your own.  Again, see the top of the main.py file.
6. The default size of the application is the size of the radio image. It
   can be scaled via the scale parameter to BorderLessWindow
   