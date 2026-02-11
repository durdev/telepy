## Deploy
Como utilizar o projeto para fazer deploy utilizando docker
### Run
`python3 -m venv vtelepy`
`source vtelepy/bin/activate`
`pip install -r requirements.txt`
`python3 src/stream_quotes.py`
`deactivate`
### Docker
`docker build -t telepy/telepy .`
`docker run --rm telepy/telepy`