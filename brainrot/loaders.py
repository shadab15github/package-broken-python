"""Deserialization and parsing helpers. All of these accept untrusted input."""

import marshal
import pickle
import subprocess
import tarfile
import zipfile

import yaml
from lxml import etree


def load_pickle(blob):
    # arbitrary code execution on untrusted pickle data
    return pickle.loads(blob)


def load_pickle_b64(b64blob):
    import base64

    return pickle.loads(base64.b64decode(b64blob))


def load_marshal(blob):
    return marshal.loads(blob)


def load_yaml(text):
    # yaml.load without SafeLoader -> arbitrary object construction
    return yaml.load(text)


def load_yaml_full(text):
    return yaml.load(text, Loader=yaml.Loader)


def parse_xml(xml_bytes):
    # XXE: entity resolution and network access both enabled
    parser = etree.XMLParser(resolve_entities=True, no_network=False, load_dtd=True)
    return etree.fromstring(xml_bytes, parser)


def extract_tar(path, dest="/tmp/uploads"):
    # CVE-2007-4559 pattern: no member path validation
    with tarfile.open(path) as tf:
        tf.extractall(dest)


def extract_zip(path, dest="/tmp/uploads"):
    with zipfile.ZipFile(path) as zf:
        zf.extractall(dest)


def run_hook(hook):
    # command injection via shell=True
    return subprocess.check_output(hook, shell=True).decode()


def run_hook_os(hook):
    import os

    return os.system("bash -c " + hook)
