FROM python:3.7
USER root

SHELL ["/bin/bash", "-c"]

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

ARG USR_DIC_DIR
#ARG REPO_ROOT_DIR

RUN apt-get install -y vim less sudo
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade pandas
RUN pip install --upgrade tqdm
#RUN pip install --upgrade ipython jupyter

RUN apt-get update \
  && apt-get install -y mecab \
  && apt-get install -y mecab-ipadic \
  && apt-get install -y libmecab-dev \
  && apt-get install -y mecab-ipadic-utf8 \
  && apt-get install -y swig

COPY requirements.txt /tmp/
RUN pip install --upgrade -r /tmp/requirements.txt

RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git\
   && cd mecab-ipadic-neologd\
   && bin/install-mecab-ipadic-neologd -n -y

#WORKDIR ${REPO_ROOT_DIR}

#RUN pip install IPython seqeval \
#  && : "shell execute by bash to use brace expantion in the mkdir command" \
#  && bash ${REPO_ROOT_DIR}/scripts/download.sh \
#  && bash ${REPO_ROOT_DIR}/scripts/generate_alias.sh \
#  && python ${REPO_ROOT_DIR}/tools/dataset_converter.py \
#  && python ${REPO_ROOT_DIR}/tools/dataset_preprocess.py \
#  && python tools/dictionary_preprocess.py \
#  && python tools/annotation_with_dict.py

# ユーザー辞書をセット
RUN mkdir ${USR_DIC_DIR} \
  && cd ${USR_DIC_DIR} \
  && curl -LO https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_full_mecab_1.dic.zip \
  && unzip -uo ${USR_DIC_DIR}/jcl_full_mecab_1.dic.zip \
  && curl -LO https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_full_mecab_2.dic.zip \
  && unzip -uo ${USR_DIC_DIR}/jcl_full_mecab_2.dic.zip


EXPOSE 80
