# Stanford NER Docker
Dockerfile with [Stanford Named Entity Recognizer](https://github.com/stanfordnlp/CoreNLP/tree/master/doc/ner) packed with HTTP server which will answer with JSON on POST or GET requests with `query` variable.

```
This Mortgage Loan Purchase Agreement, dated as of February 25, 2015, is between J.P. Morgan Chase Commercial Mortgage Securities Corp., as purchaser and Barclays Bank PLC, as seller.
```

```json
{"DATE": ["February 25, 2015"], "ORGANIZATION": ["J.P. Morgan Chase Commercial Mortgage Securities Corp.", "Barclays Bank PLC"]}
```


## Base Docker Image
* [java](https://registry.hub.docker.com/_/java/)

## Installation

1. Install [Docker](https://docs.docker.com/installation/).

2. Download [automated build](https://registry.hub.docker.com/u/lawinsider/stanford-ner-docker/) from public [Docker Hub Registry](https://registry.hub.docker.com/):

```bash
docker pull lawinsider/stanford-ner-docker
```

   alternatively, you can build an image from Dockerfile:

```bash
docker build -t="lawinsider/stanford-ner-docker" github.com/lawinsider/stanford-ner-docker
```

## Usage
Note that if you use OSX with boot2docker you will need to use `boot2docker ip` instead of localhost.

    $ docker run -d -p 4465:80 lawinsider/stanford-ner-docker
    $ curl "localhost?query=This%20Mortgage%20Loan%20Purchase%20Agreement,%20dated%20as%20of%20February%2025,%202015,%20is%20between%20J.P.%20Morgan%20Chase%20Commercial%20Mortgage%20Securities%20Corp.,%20as%20purchaser%20and%20Barclays%20Bank%20PLC,%20as%20seller."
    {"DATE": ["February 25, 2015"], "ORGANIZATION": ["J.P. Morgan Chase Commercial Mortgage Securities Corp.", "Barclays Bank PLC"]}
