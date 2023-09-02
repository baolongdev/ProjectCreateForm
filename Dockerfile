FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    git \
    git-lfs \
    wget \
    curl \
    # python build dependencies \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    # gradio dependencies \
    ffmpeg \
    # fairseq2 dependencies \
    libsndfile-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app

FROM python:3.8.0
RUN pip install --upgrade pip

COPY  ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app

ENV PYTHONPATH=/app 
#     PYTHONUNBUFFERED=1 \
#     GRADIO_ALLOW_FLAGGING=never \
#     GRADIO_NUM_PORTS=1 \
#     GRADIO_SERVER_NAME=0.0.0.0 \
#     GRADIO_THEME=huggingface \
#     SYSTEM=spaces

CMD ["python", "app.py"]