# Setup India Time
```code
sudo timedatectl set-timezone Asia/Kolkata
```
# MiniConda Setup
Download MiniConda
```code
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```
Verify the Installer
```code
sha256sum Miniconda3-latest-Linux-x86_64.sh
```

Run the Installer
```code
bash Miniconda3-latest-Linux-x86_64.sh
```

Restart your shell or run:
```code
source ~/.bashrc
```

Verify the installation:
```code
conda --version
```

Conda environments
```code
conda info --envs
```

Create and activate a test environment:
```code
conda create -n algo-env python=3.11 -y
conda activate algo-env
```




# Selenium  Setup"

### Steps :

```code
sudo yum update -y
sudo yum install -y wget curl unzip
```

### Download and install the Chrome RPM package:
```code
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

sudo yum localinstall google-chrome-stable_current_x86_64.rpm -y
```

### Verify the installation:
```code
google-chrome --version
```

### Download ChromeDriver

```code
wget https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/linux64/chromedriver-linux64.zip
```


### Extract the ChromeDriver
```code
unzip chromedriver-linux64.zip

cd chromedriver-linux64
```

### Move ChromeDriver to a system path
```code
sudo mv chromedriver /usr/bin/
sudo chmod +x /usr/bin/chromedriver
```
### Verify the installation:
```code
chromedriver --version
```

### Clean folder
```code
cd ..
rm -rf *

# Git Setup
### Install Git
```code
sudo yum install -y git
```

### Clone Repo

```code
git clone https://github.com/rushi751998/Algo_Server.git
```

### Install Requirements
```code
cd Algo_Server
pip install -r requirements.txt
```

# Test All requirements
```code
python Test_Setup.py
```


# Setup Auto file Trigger


### Set executable permissions
```code
chmod +x /home/ec2-user/Algo_Server/main.py
```

Create Shell Script

```
nano /home/ec2-user/algo_trigger.sh
```

Instructions in File

```
#!/bin/bash

cd Algo_Server
git pull origin main
cd ..

source /home/ec2-user/miniconda3/etc/profile.d/conda.sh
conda activate algo-env
python /home/ec2-user/Algo_Server/main.py

```

### Set executable permissions
```code
chmod +x /home/ec2-user/algo_trigger.sh
```

Create a new service file:
```code
sudo nano /etc/systemd/system/algo_trigger.service
```

Add the following content:
```code
[Unit]
Description=Run Conda Environment and Test Script
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user
ExecStart=/home/ec2-user/algo_trigger.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

Save, exit and Enable the service:
```code
sudo systemctl enable algo_trigger.service
sudo systemctl start algo_trigger.service
```

Reboot the instance:
```code
sudo reboot
```


For debugging
```code
sudo journalctl -u algo_trigger.service
```
For debugging
```code
nano /var/log/algo_trigger.log
```






