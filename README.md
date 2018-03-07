# artnet-unicorn-hat
Control Pimoroni Unicorn Hat and Pimoroni Mote LEDs
using the Art-Net or OPC protocol.

Art-Net and Open Pixel Control (OPC aka FadeCandy) are protocols for
controlling lights over a network.
Glediator is an example of one program that controls LEDs on one or
more Art-Net nodes. An Art-Net node drives the LEDs.
In this example, Glediator runs on a laptop and controls a Pi with LEDs.
The Pi is the Art-Net node.
Hyperion is an ambient light controller for Kodi. It detects the colors
that are being presented on the Kodi screen and sends information about 
the colour changes on the boarder of the screen using a variety of
mechanisms including OPC (FadeCandy)

A Pimoroni Unicorn Hat is an add-on board for a Raspberry Pi+/2 with an 
8 by 8 grid of ws281x LEDs.
A Pimoroni Mote is a USB attached device with up to 4 sets of 16 LEDs attached

http://www.solderlab.de/index.php/software/glediator

https://en.wikipedia.org/wiki/Art-Net

https://hyperion-project.org/

http://openpixelcontrol.org/

## Preliminary

The Unicorn Hat or Mote must be installed and working on the Pi with the
Pimoroni supplied Python software. Make sure this works before graduating
to Art-Net.

http://learn.pimoroni.com/tutorial/unicorn-hat/getting-started-with-unicorn-hat
https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-mote

Note: If you are trying to use Mote on a Raspberry Pi running OSMC then there
are special instructions mentioned below

## Install libraries on the Pi

Do this only once to install the Python twisted libraries.
```
sudo pip install twisted
```
For Pimoroni Mote you also need to install some additional libraries which
you can do using the Pimoroni install script.
(at the time of writing this (19 October 2017) the Pimoroni install script
does not work on OSMC so use the command below)
```
sudo pip install pyserial mote numpy
```


## Run Art-Net server on the Pi
The following command runs the Art-Net server turning the Pi
into an Art-Net node. 
Many programs can send LED values to an Art-Net node. Glediator is one such
program.

```
sudo python artnet-server.py
note if using Pimoroni Mote then you do not need to use "sudo" at the start
```

## Glediator

See the Glediator download page to download and install Glediator.
If you see errors about missing binary RXTX, ignore them. In this case,
Glediator controls the LEDs using network packets, not serial communcations.

Glediator is designed to work with many different LED arrays so it must
be told the dimensions and arrangements of the LEDs. It must also be
told the IP address of the Pi with the Unicorn Hat.

### Change IP address in patch file
Open the Glediator patch file artnet-pimoroni-unicorn-hat.gled in your
favorite editor. nano works fine. Change the IP address to the IP address
of the Pi.

This how the IP address 192.168.1.231 looks like in the file

```
Patch_Uni_ID_0_IP1=192
Patch_Uni_ID_0_IP2=168
Patch_Uni_ID_0_IP3=1
Patch_Uni_ID_0_IP4=231
```

Close and save the file.

### Set matrix size
In Glediator change the matrix size to 8 by 8.

At the Glediator main screen, select Options | Matrix Size

Size_X = 8 Size_Y = 8

### Set Art-Net mode
At the Glediator main screen, select Options | Output

At the Output Options screen:

```
Output Mode: Artnet
Mapping Mode: Single_Pixels
```

Ignore the rest in the top half of the screen. Ignore the left bottom options
which are for serial ports.

In the right bottom options click on Patch ArtNet/TMP2.Net

At the "Artnet & TPM2.Net Patcher" screen, load artnet-pimoroni-unicorn-hat.gled

Click on Done

Back at the Output Options screen, click on Apply Changes.

Click on "Open Socket". Glediator will start sending pixel values to the Pi.

Click on Done to get back to the main screen.

At this point, the control panel can be used to generate new patterns.

## PixelController

https://github.com/neophob/PixelController/releases

PixelController is another LED pattern generator with Art-Net output. After
unzipping pixelcontroller-distribution-2.1.0-RC1.zip change into the directory
pixelcontroller-distribution-2.1.0-RC. Copy config.properties from this
repo to the directory data.

Edit data/config.properties to set the IP address of the Pi.

```
# Change the following line to match the IP of your Pi
artnet.ip=192.168.1.231
```

Next run the program. The Unicorn Hat should immediately show pixel patterns.

```
unzip pixelcontroller-distribution-2.1.0-RC1.zip
cd pixelcontroller-distribution-2.1.0-RC
cp ~/artnet-unicorn-hat/config.properties data/
nano data/config.properties
java -jar PixelController.jar
```

## Open Pixel Control Protocol

Support included for Open Pixel Control protocol on TCP port 7890. See
https://github.com/zestyping/openpixelcontrol for the OPC protocol
specification.

Do not use OPC and Art-Net at the same time.
This will just produce garbage on the LEDs.
Near the top of the artnet-server.py file there are some settings that you
can adjust.

In this version the defaults are for Pimoroni Mote being driven by
OPC (FadeCandy) for Hyperion/Kodi.
If you want to change this then edit the file and change to what you want.
Note - do not enable PimUnicorn and PimMote at the same time.
The lines to look for in artnet-server.py are:
```
PimUnicorn = False
PimMote = True

SupportArtNet = False
```



### Example OPC programs to drive the LEDs

Hyperion (for Kodi)
A sample Hyperion configuration file is included in the repository.
This one assumes that the LEDs are arranged around the screen
except for the bottom.
Left bottom (as you look at front of screen) is pixel 1, top left is 17 (stick 2),
top right is 48 (far end of stick 3) and bottom right is 64 (far end of stick 4).
If you want a different configuration then you can generate your own using HyperCon
and then push the hyperion.config.json file using HyperCon to the Hyperion system.
Note - the json file must have that name unless you configure Hyperion to be
started with config file name in command line.
On OSMC (and possibly other Linux distributions) the config file needs to be in the
directory /etc/hyperion/

Note: The LEDs will not turn off when you turn off the screen.
However, you will probably find that they do turn off when the Kodi screensaver kicks
in when on home page (unless you have a screen saver with bright edges!)

Many Open Pixel Control and Fade Candy examples work. Be sure to
modify the examples with the Raspi IP address.

The following examples from https://github.com/zestyping/openpixelcontrol work.

    python_clients/
            lava_lamp.py,miami.py,nyan_cat.py,sailor_moon.py,spatial_stripes.py

            ```
            $ ./lava\_lamp.py -l grid8x8.json -s <Raspi IP addr>:7890 -f 20
            ```

The Fadecandy grid8x8 Processing examples at https://github.com/scanlime/fadecandy work. These examples show how
to create interactive LED displays. Edit the PDE file to add the Raspi IP address.

    examples/processing/
        grid8x8_dot, grid8x8_noise_sample, grid8x8_orbits, grid8x8_wavefronts

## OSMC on Raspberry Pi Quick Start
Brief instructions for getting this to work on OSMC on Raspberry Pi.
Only basics given here - so much knowledge or willingness to search is assumed.

Install HyperCon on desktop/laptop machine
Use HyperCon to install Hyperion on Raspberry Pi
 If you get GNUTLS errors when it tries to fetch Hyperion just pause and try again
 Do not worry about installation errors referring to X11

* Now install the environment for building some of the modules
The installation of some of the Python modules performs some compilations locally, but OSMC does
 not come with the needed tools. So install them first:
 ```
 sudo apt-get update
 sudo apt-get install build-essential
 export ARCH=arm
 export CROSS_COMPILE=/usr/bin
 sudo apt-get install python-dev

* Next step is to install the Pimoroni Mote Python files
```
sudo pip install pyserial mote
```
* Note - pyserial not serial and watch out because pyserial has a name clash with serial (which does something totally different)
* ALso the NumPy module is used to compare arrays - this can be installed using
```
sudo pip install numpy
```
* Can give errors during the process and takes a long time (e.g. 10 minutes on RPi3)
Possible errors ...
 Failed building wheel for numpy
and
 Failed cleaning build dir for numpy
however, if they are the only errors then it should still work ...

An alternative approach that I did not try but will be a lot faster if it works
sudo apt-get install python-numpy


* Then get artnet-server and related files onto the OSMC machine
* One way to do this is to login via SSH to your OSMC system
  Assuming that you are now in /home/osmc directory ...
  ```
  sudo apt-get install wget unzip
  wget https://github.com/PaulWebster/artnet-unicorn-hat/archive/mote.zip
  unzip mote.zip
  cp artnet-unicorn-hat-mote/artnet-server.py .
  ```
 * Then set-up the Hyperion configuration file (must have installed Hyperion first)
 ```
 cp artnet-unicorn-hat-mote/hyperion.config.json /etc/hyperion
 ```
 * Then install the modules required by artnet-server
 ```
 then you can install Twisted
 ```
 sudo pip install twisted
 ```
 * Next step is to set artnet-server.py to start on boot
 ```
 sudo cp artnet-unicorn-hat-mote/artnet-server.service /lib/systemd/system/artnet-server.service
 sudo systemctl enable artnet-server
 sudo systemctl start artnet-server
 ```

* Then shutdown your Raspi, plug in the Mote stick controller, power on Raspi

