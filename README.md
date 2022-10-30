clone the repo from
```
git clone
```
run the following commands
```
$ sudo mv ~/.search_server/server.service /etc/systemd/system/server.service
$ sudo systemctl enable /etc/systemd/system/server.service
$ sudo systemctl daemon-reload
$ sudo service server start
```

```
$ sudo mkdir /usr/local/lib/server
$ sudo mv ~/search_server/server.py /usr/local/lib/server/server.py
```

Now your script will be put into service and will be started. To check for errors or not, you can run this command:
```
$ sudo service server status
```

To stop the script, you can run the command:
```
$ sudo service server stop
```