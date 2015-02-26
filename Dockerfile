FROM java:8
MAINTAINER Dmitry Sadovnychyi (ner@dmit.ro)

RUN apt-get install -y \
      unzip \
    && apt-get clean  && \
    rm -rf /var/lib/apt/lists/*

ADD http://nlp.stanford.edu/software/stanford-ner-2015-01-29.zip ner.zip
RUN unzip ner.zip

WORKDIR /stanford-ner-2015-01-30

ADD run.py run.py

ENTRYPOINT ["python", "-u", "/stanford-ner-2015-01-30/run.py"]
EXPOSE 80
