FROM python:latest
WORKDIR /api
COPY . /api
RUN pip install -r requirements.txt
EXPOSE 6000
CMD [ "flask", "run" , "-p", "6000"]