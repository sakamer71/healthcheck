# HEALTHCHECK

## Track calories and nutrition using AI

## to run
source .venv/bin/activate
fastapi dev app/main.py

## routes
http://localhost:8000/api/calorie_count/{meal}

## Structure
```
healthcheck
├── README.md
├── __pycache__
│   └── app.cpython-311.pyc
├── app
│   ├── __pycache__
│   │   └── main.cpython-311.pyc
│   ├── api
│   │   ├── models
│   │   └── routes
│   ├── main.py
│   └── utils.py
├── index.html
├── static
│   └── images
│       └── favicon.ico
├── templates
└── tests
```

run using
docker run -d -p 9999:8000 -v ~/.aws:/root/.aws  healthcheck:0.1 