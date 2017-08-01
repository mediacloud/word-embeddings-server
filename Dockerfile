# gunicorn-flask
MAINTAINER Rahul Bhargava<rahulb@mit.edu>

RUN apt-get update
RUN apt-get install -y python python-pip python-virtualenv gunicorn

# Setup flask application
RUN mkdir -p /deploy/app
COPY gunicorn_config.py /deploy/gunicorn_config.py
COPY app /deploy/app
RUN pip install -r /deploy/app/requirements.txt

# Download GoogleNews model
RUN wget https://github.com/mmihaltz/word2vec-GoogleNews-vectors/blob/master/GoogleNews-vectors-negative300.bin.gz \
    -P /deploy/app/models/

# Configure the app
WORKDIR /deploy/app
EXPOSE 5000

# Start gunicorn
CMD ["/usr/bin/gunicorn", "--config", "/deploy/gunicorn_config.py", "server:app"]
