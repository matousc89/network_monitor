#Deriving the latest base image
FROM python:3.7.17-alpine

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

RUN apk update \
    apk add \
    build-base \
    postgresql \
    postgresql-dev \
    libpq \
    pip \
    python-numpy \
    python-scipy 

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src

#to COPY the remote file at working directory in container
COPY . .
# Now the structure looks like this '/usr/app/src/test.py'


#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

CMD [ "python", "./run.py"]