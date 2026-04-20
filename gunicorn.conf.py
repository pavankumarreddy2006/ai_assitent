workers = 3
worker_class = "sync"          # Flask doesn't need UvicornWorker
bind = "0.0.0.0:8000"
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"