bind = "0.0.0.0:5050"
workers = 4
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
access_log_format = '%(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
