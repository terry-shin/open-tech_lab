FROM python:3.8
USER root

SHELL ["/bin/bash", "-c"]

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
    numpy \
    scipy \
    matplotlib \
    ipython \
    scikit-learn \
    pandas \
    pillow \
    mglearn \
    requests \
    pyperclip \
    beautifulsoup4　\
    selenium \
    phantomjs \
    jupyterlab

# Chromeドライバーのダウンロード
RUN wget -q -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Chromeのインストール
RUN apt-get install -y libgbm1 libappindicator3-1 libappindicator1 fonts-liberation libasound2 libnspr4 libnss3 libxss1 lsb-release xdg-utils libfontconfig
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb

CMD bash -c "jupyter-lab --notebook-dir=/usr/local/src/notebooks --ip='0.0.0.0' --no-browser --allow-root --NotebookApp.token=''"
