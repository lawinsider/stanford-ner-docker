#!/usr/bin/env python

import os
import re
import json
import socket
import urlparse
import subprocess
import contextlib
import BaseHTTPServer
from collections import OrderedDict
from itertools import groupby
from operator import itemgetter


STANFORD_PARSER = os.path.abspath('stanford-ner.jar')
STANFORD_MODEL = os.path.abspath(
  'classifiers/english.all.7class.distsim.crf.ser.gz')
SLASHTAGS_EPATTERN = re.compile(r'(.+?)/([A-Z]+)?\s*')
XML_EPATTERN = re.compile(r'<wi num=".+?" entity="(.+?)">(.+?)</wi>')
INLINEXML_EPATTERN = re.compile(r'<([A-Z]+?)>(.+?)</\1>')


def start_ner_server(parser, model):
  devnull = open('/dev/null', 'w')
  return subprocess.Popen([
    'java',
    '-Xmx900m',
    '-cp',
    parser,
    'edu.stanford.nlp.ie.NERServer',
    '-loadClassifier',
    model,
    '-outputFormat',
    'inlineXML'
  ], stdout=devnull, stderr=devnull)


@contextlib.contextmanager
def tcpip4_socket(host, port):
  """Open a TCP/IP4 socket to designated host/port."""
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    s.connect((host, port))
    yield s
  finally:
    try:
      s.shutdown(socket.SHUT_RDWR)
    except socket.error:
      pass
    except OSError:
      pass
    finally:
      s.close()


class NER(object):
  """Wrapper for server-based Stanford NER tagger."""

  def __init__(self, host='localhost', port=4465, output_format='inlineXML'):
    if output_format not in ('slashTags', 'xml', 'inlineXML'):
      raise ValueError('Output format %s is invalid.' % output_format)
    self.host = host
    self.port = port
    self.oformat = output_format

  def tag_text(self, text):
    """Tag the text with proper named entities token-by-token.

    Args:
      text: Raw text string to tag.

    Returns:
      Tagged text in given output format.
    """
    for s in ('\f', '\n', '\r', '\t', '\v'):
      text = text.replace(s, '')
    text += '\n'
    with tcpip4_socket(self.host, self.port) as s:
      s.sendall(text)
      tagged_text = s.recv(10 * len(text))
    return tagged_text

  def _parse_entities(self, tagged_text):
    """Return a list of entity tuples (entity_type, entity) parsed
    from inlineXML-format tagged text.

    Args:
      tagged_text: inlineXML-format tagged text.
    """
    return (m.groups() for m in INLINEXML_EPATTERN.finditer(tagged_text))

  def _collapse_to_dict(self, pairs):
    """Return a dictionary mapping the first value of every pair
    to a collapsed list of all the second values of every pair.

    Args:
      pairs: List of (entity_type, token) tuples.
    """
    d = dict((first, map(itemgetter(1), second)) for (first, second)
             in groupby(sorted(pairs, key=itemgetter(0)), key=itemgetter(0)))
    return {k: list(OrderedDict.fromkeys(v)) for k, v in d.iteritems()}

  def get_entities(self, text):
    """Return all the named entities in text as a dict.

    Args:
      text: String to parse entities.

    Returns:
      A dict of entity type to list of entities of that type.
    """
    tagged_text = self.tag_text(text)
    entities = self._parse_entities(tagged_text)
    return self._collapse_to_dict(entities)

  def json_entities(self, text):
    """Return a JSON encoding of named entities in text.

    Args:
      text: string to parse entities.

    Returns:
      A JSON dump of entities parsed from text.
    """
    return json.dumps(self.get_entities(text))


class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  ner = NER()

  def parse_query(self):
    length = int(self.headers['content-length'])
    qs = urlparse.parse_qs(self.rfile.read(length).strip())
    query = qs.get('query', [None])[0]
    return query

  def build_response(self, query):
    if query is None:
      return self.send_response(400)
    try:
      entities = self.ner.json_entities(query)
    except socket.error as e:
      print e
      return self.send_response(502)
    except Exception as e:
      print e
      return self.send_response(500)

    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    return self.wfile.write(entities)

  def do_POST(self):
    return self.build_response(self.parse_query())

  def do_GET(self):
    query = urlparse.parse_qs(urlparse.urlparse(self.path).query).get(
      'query', [None])[0]
    return self.build_response(query)


if __name__ == '__main__':
  print 'Starting Stanford NER TCP server...'
  start_ner_server(STANFORD_PARSER, STANFORD_MODEL)
  print 'Starting HTTP proxy server...'
  try:
    server = BaseHTTPServer.HTTPServer(('0.0.0.0', 80), HttpHandler)
    server.serve_forever()
  except KeyboardInterrupt:
    print('Stopping NER server..')
    server.socket.close()
