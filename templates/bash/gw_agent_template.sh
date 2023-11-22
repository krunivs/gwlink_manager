#!/bin/bash
set -e

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

CLUSTER={cluster}
CENTER_IP={manager_ip}
CENTER_PORT={manager_port}
AGENT_PORT={agent_port}
AMQP_IP={amqp_ip}
AMQP_PORT={amqp_port}
AMQP_ID=admin
AMQP_PWD=1234
AMQP_HOST=/
INSTALL_DIR=/var/local
REPO_URL=https://github.com/krunivs/gw_agent.git
SERVICE_FILE=/etc/systemd/system/gw_agent.service
PROJECT=gw_agent

# if service exist, remove it
if service_exists $PROJECT; then
    systemctl stop $PROJECT
    systemctl disable $PROJECT
    systemctl daemon-reload
fi

# check python runtime
info "Create gw_agent install dir, $INSTALL_DIR"
mkdir -p $INSTALL_DIR

# gw-agent git clone
cd $INSTALL_DIR
info "Git clone gw_agent package, $INSTALL_DIR"

if [[ -d "$INSTALL_DIR/gw_agent" ]]; then
  rm -rf $INSTALL_DIR/gw_agent
fi
git clone $REPO_URL

# install python packages
info "Install required python package, $INSTALL_DIR"
cd $INSTALL_DIR/gw_agent
pip3 install -r requirements.txt

# create gw-agent config.ini
info "Create gw_agent config.ini, $INSTALL_DIR/gw_agent/static/config.ini"
cat << EOF | sudo tee $INSTALL_DIR/gw_agent/static/config.ini
[ClusterSection]
cluster_id=$CLUSTER
center=http://$CENTER_IP:$CENTER_PORT
http=http://$CENTER_IP:$CENTER_PORT
amqp_ip=$AMQP_IP
amqp_port=$AMQP_PORT
amqp_id=admin
amqp_pwd=1234
amqp_vhost=/
https=
token=
EOF

# create gw_agent.service
info "Create gw-gw_agent service, $SERVICE_FILE"
cat << EOF | sudo tee $SERVICE_FILE
[Unit]
Description=GEdge Gateway Agent
ConditionPathExists=$INSTALL_DIR/gw_agent
After=network.target

[Service]
User=root
Group=root
LimitNOFILE=1048576
Restart=on-failure
RestartSec=1

ExecStart=/usr/bin/sudo /usr/bin/python3 manage.py runserver 0.0.0.0:$AGENT_PORT
WorkingDirectory=$INSTALL_DIR/gw_agent
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=gw_agent

[Install]
WantedBy=multi-user.target
EOF

# delete submariner components
info "Delete submariner components"
cd $INSTALL_DIR/gw_agent/scripts
./delete_subm.sh || true

# enable and start service
info "Register and run gw_agent service"
systemctl daemon-reload
systemctl start gw_agent
systemctl enable gw_agent
systemctl status gw_agent