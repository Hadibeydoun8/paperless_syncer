FROM python:3
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD config.json /
ADD main.py /
ADD APIHandler.py /
CMD [ "python", "./main.py" ]