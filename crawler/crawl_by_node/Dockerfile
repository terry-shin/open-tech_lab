FROM node:12
USER root

SHELL ["/bin/bash", "-c"]

WORKDIR /usr/local/src/app

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install locales fonts-ipafont fonts-ipaexfont && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
RUN apt-get -y install -y --no-install-recommends git
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

RUN apt-get install -y libx11-xcb1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libnss3 \
    libxss1
RUN apt-get -y install nodejs

COPY package*.json ./
RUN npm install
RUN npm init -y
RUN npm install -g nodemon

EXPOSE 8080

COPY work/app.js ./
CMD bash -c "nodemon work/app.js"
