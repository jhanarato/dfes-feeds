# DFES RSS feed parser

A Python package for the Western Australian [Deparment of Fire and Emergency Services ](https://dfes.wa.gov.au/) fire ratings and total fire ban alerts. These are published via RSS and are stored via the command `dfes fetch`. `dfes show` will show the latest total fire bans. 

This package can be installed via pipx:

`pipx install git+https://github.com/jhanarato/dfes-feeds.git --python python3.11`

This will download the latest RSS and store it in the repository, then display the total fire bans:

```commandline
jr@JR-Desktop:~$ dfes fetch && dfes show
Total Fire Bans
Issued: 2024-02-22 16:38:00+08:00
Declared for: 2024-02-23
Pilbara / Ashburton
Pilbara / Exmouth
Pilbara / Karratha
```

Note that the repository defaults to `~/.dfes`.