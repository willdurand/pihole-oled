# pihole-oled


## Installation

```
$ sudo apt-get install libopenjp2-7 libtiff5 python3-pip
```

```
$ pip3 install --user pipenv
```

```
$ pipenv install
```

```
$ sudo cp pihole-oled.service /etc/systemd/user/
```

```
$ sudo systemctl enable /etc/systemd/user/pihole-oled.service
```

```
$ sudo systemctl start pihole-oled.service
```
