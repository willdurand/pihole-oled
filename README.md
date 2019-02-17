# pihole-oled

<p align="center"><img src="./res/pihole-oled-demo.gif"></p>

## Hardware

The OLED display is connected _via_ I2C with 4 wires: `SDA`, `SCL`, `3.3V` and
`GND`. There is no `reset` pin. The "HAT" is made with a 8-pin female header, a
piece of proto-board and short wires. There is nothing fancy here.

## Installation

:warning: This project requires a Raspberry Pi with
[Pi-hole](https://pi-hole.net/) installed, the [I2C bus
enabled](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c)
and Python 3.5.

### Software requirements

If you do not have `pip3` installed, start by installing it:

```
sudo apt-get install python3-pip
```

If you do not have `pipenv` installed, install it too:

```
pip3 install --user pipenv
```

Note: the command above keeps everything into a `~/.local` directory. You can
update the current user's `PATH` by adding the following lines into your
`.bashrc` (or equivalent):

```
export PY_USER_BIN="$(python -c 'import site; print(site.USER_BASE + "/bin")')"
export PATH="$PY_USER_BIN:$PATH"
```

Now install a few libraries for
[Pillow](https://pillow.readthedocs.io/en/stable/index.html):

```
sudo apt-get install libopenjp2-7 libtiff5
```

### Project installation

Clone this project:

```
git clone https://github.com/willdurand/pihole-oled.git /home/pi/pihole-oled
```

Install the python dependencies:

```
cd /home/pi/pihole-oled
pipenv install
```

If you plug the OLED display and run the command below, you should see some
information on the display:

```
pipenv run python3 main.py
```

You can exit the script with <kbd>ctrl</kbd>+<kbd>c</kbd>.

### Systemd configuration

You can install a `systemd` service by copying the provided configuration file
using the command below. This service will automatically run the python script
mentioned in the previous section on boot:

```
sudo cp pihole-oled.service /etc/systemd/user/
```

Enable, then start the `pihole-oled.service`:

```
sudo systemctl enable /etc/systemd/user/pihole-oled.service
sudo systemctl start pihole-oled.service
```


## Dev corner

This sections is only relevant if you intent to work on this project.

We use
[conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html)
to ship a (hopefully) reproducible environment to work on this project. Start by
installing `conda`, then create the environment for this project:

```
conda env create -f environment.yml
```

Do not forget to enable this environment:

```
conda activate
```

You should have `python3` (3.5) and `pipenv` available now.


## License

This project is released under the MIT License. See the bundled [LICENSE
file](./LICENSE) for details.
