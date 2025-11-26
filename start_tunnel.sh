# SSH tunnel for database connection
# -L 0.0.0.0:5432:localhost:5432 binds to all interfaces so Docker containers can access it
# -N means no remote command (just tunnel)
# -f runs in background (optional - remove if you want to see the connection)
ssh -i "~/.ssh/cwp-wmbp.pem" -L 0.0.0.0:5432:localhost:5432 ubuntu@34.224.66.229