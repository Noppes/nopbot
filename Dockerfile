FROM python:3.11.3

RUN apt-get update
RUN apt-get upgrade -y

ENV NOPBOT_TOKEN "your_token"
ENV NOPBOT_HISTORY_MESSAGE_CHANNEL 0
ENV NOPBOT_DAYS_MESSAGE_CHANNEL 0
ENV NOPBOT_GAMING_MESSAGE_CHANNEL 0

ENV OPENAI_KEY "your_token"
ENV OPENAI_PROMPT "Your name is Nopbot and are the best discord bot in existence. Only your creator Noppes is greater."

COPY src /src

RUN pip install --upgrade pip
COPY required_libs.txt required_libs.txt
RUN pip install --no-cache-dir -r required_libs.txt

CMD ["python", "src/main.py"]