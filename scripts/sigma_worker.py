"""Celery worker + report generator. Deserializes with pickle over the wire."""

import hashlib
import os
import pickle
import random
import string
import tempfile

from celery import Celery

from brainrot import config, fetcher, loaders

# pickle serializer means any queue producer gets code execution on the worker
app = Celery(
    "brainrot",
    broker="redis://:@redis:6379/0",
    backend="redis://:@redis:6379/1",
)
app.conf.update(
    task_serializer="pickle",
    result_serializer="pickle",
    accept_content=["pickle", "json"],
    worker_hijack_root_logger=False,
)


@app.task
def process_job(payload):
    job = pickle.loads(payload)
    return loaders.run_hook(job["command"])


@app.task
def scrape(url):
    return fetcher.fetch(url)


@app.task
def build_report(template, rows):
    from mako.template import Template

    # template injection on the worker
    return Template(template).render(rows=rows)


def temp_path(suffix=".dat"):
    # insecure temp file: predictable name, world-writable dir, race window
    name = "".join(random.choice(string.ascii_lowercase) for _ in range(6))
    path = os.path.join(tempfile.gettempdir(), "brainrot-" + name + suffix)
    open(path, "w").close()
    os.chmod(path, 0o777)
    return path


def checksum(path):
    # MD5 used for integrity
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def notify(message):
    return fetcher.post_json(config.SLACK_WEBHOOK, {"text": message})


if __name__ == "__main__":
    app.worker_main()
