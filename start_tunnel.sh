#!/bin/bash

# SSH tunnel for database connection
# -L 0.0.0.0:5432:localhost:5432 binds to all interfaces so Docker containers can access it
# -N means no remote command (just tunnel)
# -f runs in background (optional - remove if you want to see the connection)

# Load EC2 config
CONFIG_FILE=".ec2-deploy.conf"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "ERROR: $CONFIG_FILE not found. Run './ec2-deploy.sh --setup' first."
    exit 1
fi

ssh -i "$SSH_KEY" -L 0.0.0.0:5432:localhost:5432 "$EC2_USER@$EC2_HOST"