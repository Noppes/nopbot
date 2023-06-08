FROM python:3.11.3

ENV NOPBOT_TOKEN "your_token"
ENV NOPBOT_MESSAGE_CHANNEL 0

COPY src /

COPY required_libs.txt required_libs.txt
RUN pip install --no-cache-dir -r required_libs.txt

CMD ["python", "main.py"]