FROM fedora:25

RUN dnf update -y && \
    dnf install -y python3-pip git && \
    git clone https://github.com/vrutkovs/reddit-to-telegram /reddit-telegram && \
    cd reddit-telegram && \
    pip3 install -r requirements.txt && \
    dnf clean all

WORKDIR /reddit-telegram

CMD ["python3", "telegram_poster.py"]
