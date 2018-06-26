FROM java:8
MAINTAINER Dmitry Sadovnychyi (ner@dmit.ro)

RUN apt-get install -y \
      unzip \
    && apt-get clean  && \
    rm -rf /var/lib/apt/lists/*

ENV STANFORD_NER_VERSION=stanford-ner-2018-02-27

ADD "https://nlp.stanford.edu/software/${STANFORD_NER_VERSION}.zip" ner.zip
# If we have the ner archive locally (dev), build from it to save time
# ADD "${STANFORD_NER_VERSION}.zip" ner.zip

RUN unzip ner.zip && rm ner.zip
WORKDIR "${STANFORD_NER_VERSION}"

ADD run.py ./

CMD ["python", "-u", "./run.py"]
EXPOSE 80
