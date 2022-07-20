FROM node:16

USER root

WORKDIR /home/app

RUN echo 'linux update'; \
  apt update && \
  apt upgrade -y

RUN echo 'vue-cli install'; \
  npm install -g @vue/cli

RUN echo 'firebase-tools install'; \
  npm install -g firebase-tools

RUN echo 'firebase install'; \
  npm install --save firebase

RUN echo 'vuetify install'; \
  npm install vuetify
