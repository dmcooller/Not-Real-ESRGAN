# Run as linux service

## Create script

Create srcipt in `/usr/bin/esrgan` to start, stop and restart the service.

```bash
nano /usr/bin/esrgan
```

Replace `/root` with yor path to the `Not-Real-ESRGAN` directory. Content:
```
#!/bin/bash

case "$1" in
    start)
        echo "Starting Not-Real-ESRGAN"
        cd /root/Not-Real-ESRGAN
        sudo ./venv/bin/python3 ./web.py &
        ;;
    stop)
        echo "Stopping Not-Real-ESRGAN"
        kill $(ps aux | grep -m 1 '/root/Not-Real-ESRGAN/venv/bin/python3 /root/Not-Real-ESRGAN/web.py' | awk '{ print $2 }')
        ;;
    restart)
        echo "Restarting Not-Real-ESRGAN"
        sudo esrgan stop
        sudo esrgan start
        ;;
    *)
        echo "Usage: esrgan start|stop|restart"
        exit 1
        ;;
esac
exit 0
```

```bash
sudo chmod +x /usr/bin/esrgan
```

## Create service

```bash
nano /lib/systemd/system/esrgan.service
```

Content:
```
[Unit]
Description=Not-Real-ESRGAN
After=network.target

[Service]
ExecStart=sudo esrgan start
ExecStop=sudo esrgan stop
Type=forking
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```


Reload the systemd daemon:
```bash
sudo systemctl daemon-reload
```

Start the service:
```bash
sudo systemctl start esrgan
```

If everything is working as expected, enable the service to start on boot:
```bash
sudo systemctl enable esrgan.service
```