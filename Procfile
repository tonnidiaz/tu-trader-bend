# web: gunicorn --worker-class eventlet -w 1 app:ap
web: gunicorn -b 0.0.0.0:8080 --workers $(($(nproc --all) * 2 + 1)) app:app --preload --timeout 3600