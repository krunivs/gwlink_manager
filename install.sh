#!/bin/bash
PROJECT=gwlink_manager
SERVICE_FILE=/etc/systemd/system/$PROJECT.service
REPOSITORY=https://github.com/krunivs/$PROJECT.git
PROJECT_ROOT=/usr/local/$PROJECT
# HTTP_HOST=
# HTTP_PORT=

function error() {
    local message=$1
    echo -e "[ERROR] $message"
    exit 1
}

function info() {
    local message=$1
    echo -e "[INFO] $message"    
}

function service_exists() {
    local n=$1
    if [[ $(systemctl list-units --all -t service --full --no-legend "$n.service" | sed 's/^\s*//g' | cut -f1 -d' ') == $n.service ]]; then
        return 0
    else
        return 1
    fi
}

if [[ -z "$HTTP_HOST" ]]; then
    error "Not found environment variable "HTTP_HOST". You should set HTTP_HOST variable with filling internet accessible host address(i.e., domain, ip)"
fi

if [[ -z $HTTP_PORT ]]; then
    error "Not found environment variable "HTTP_PORT". You should set HTTP_PORT variable with filling internet accessible host TCP port"
fi

info "Clean local $PROJECT"

# if service exist, remove it
if service_exists $PROJECT; then
    systemctl stop $PROJECT
    systemctl disable $PROJECT
    systemctl daemon-reload
fi

# if service file exist, remove it
if [[ -f $SERVICE_FILE ]]; then
    rm -rf $SERVICE_FILE
fi

# if project is not exist, git clone from gwlink_manager repository
if [[ ! -f $PROJECT_ROOT ]]; then
    cd /usr/local
    git clone $REPOSITORY
fi

info "Install $PROJECT"
# install python packages
pip3 install -r $PROJECT_ROOT/requirements.txt
if [ ! $? -eq 0 ]; then
    error "Failed to install gwlink_manager python library"
fi

# deploy rabbitmq service & pod
# check rabbitmq service & pod
info "Install $PROJECT MQTT"
kubectl apply -f rabbitmq.yaml

# install service
info "Install $PROJECT service"
cat << EOF | sudo tee $SERVICE_FILE
[Unit]
Description=GEdge Gateway Link Manager
ConditionPathExists=$PROJECT_ROOT/manage.py
After=network.target

[Service]
User=root
Group=root
Environment="GWLINK_MANAGER_HOST=$HTTP_HOST"

LimitNOFILE=1048576
Restart=on-failure
RestartSec=1
 
ExecStart=/usr/bin/sudo /usr/bin/python3 manage.py runserver 0.0.0.0:$HTTP_PORT
WorkingDirectory=$PROJECT_ROOT
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=$PROJECT

[Install]
WantedBy=multi-user.target
EOF

info "Activate $PROJECT service"
systemctl daemon-reload
systemctl start $PROJECT
systemctl enable $PROJECT
systemctl status $PROJECT