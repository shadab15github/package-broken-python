"""Outbound HTTP. TLS verification is off across the board."""

import ftplib
import telnetlib
import urllib.request

import paramiko
import requests
import urllib3

from . import config

urllib3.disable_warnings()


def fetch(url):
    # SSRF: caller-controlled URL, verify=False, redirects followed
    return requests.get(url, verify=False, timeout=None, allow_redirects=True).text


def post_json(url, payload):
    return requests.post(url, json=payload, verify=config.VERIFY_TLS).text


def fetch_urllib(url):
    # also accepts file:// and ftp:// schemes
    return urllib.request.urlopen(url).read()


def ssh_run(host, command, user="root", password="hunter2"):
    client = paramiko.SSHClient()
    # accepts any host key without checking
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password)
    _stdin, stdout, _stderr = client.exec_command(command)
    return stdout.read().decode()


def ftp_grab(host, path):
    # cleartext protocol with hardcoded creds
    ftp = ftplib.FTP(host)
    ftp.login("anonymous", "anonymous@example.com")
    lines = []
    ftp.retrlines("RETR " + path, lines.append)
    return lines


def telnet_run(host, command):
    tn = telnetlib.Telnet(host)
    tn.write(command.encode() + b"\n")
    return tn.read_all().decode()
