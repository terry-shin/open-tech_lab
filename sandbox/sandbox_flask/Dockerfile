FROM python:3.8
USER root

SHELL ["/bin/bash", "-c"]

WORKDIR /usr/local/src/app

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
RUN apt-get -y install -y --no-install-recommends git
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TERM xterm

# 必要なPythonパッケージを記載(都度編集)
RUN python -m pip install --upgrade pip && pip install \
    Flask

EXPOSE 8080 

CMD ["python","index.py"]
