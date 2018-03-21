FROM python:3.6

# ssh
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
	&& apt-get install -y --no-install-recommends openssh-server \
	&& echo "$SSH_PASSWD" | chpasswd

RUN pip install numpy

WORKDIR /tmp
RUN git clone https://github.com/facebookresearch/fastText.git
WORKDIR /tmp/fastText
RUN pip install .

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

COPY docker/sshd_config /etc/ssh/
COPY docker/init.sh /usr/local/bin/

RUN chmod u+x /usr/local/bin/init.sh
EXPOSE 8000 2222
ENTRYPOINT ["init.sh"]
