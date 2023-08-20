FROM python3

# ENV TZ='Asia/Kolkata'

# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && mkdir /code

# ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait

# RUN chmod +x /wait

WORKDIR /code

EXPOSE 8080 6000

COPY requirements.txt /code/

# RUN mkdir static files files/temp_cas files/account_opening_form files/mandates files/reports files/rebalancing && rm -rf .git

# ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update

# RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

#RUN apt-get -y --no-install-recommends install python3-pip python3-dev tzdata libpq-dev gcc
RUN apt-get -y --no-install-recommends install python3-pip 

RUN apt-get -y --no-install-recommends install python3-dev 

RUN apt-get -y --no-install-recommends install wget tzdata ffmpeg poppler-utils libpq-dev gcc libmagic-dev

RUN rm -rf /var/lib/apt/lists/* && pip3 install --upgrade setuptools 

RUN pip3 install -r requirements.txt --no-cache-dir && apt-get autoclean
# && pip3 install uwsgi && echo "y" |  apt-get autoremove gcc --purge && echo "y" | apt-get autoclean


# RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb && apt-get update && apt-get install -y --no-install-recommends ./wkhtmltox_0.12.6-1.focal_amd64.deb && rm ./wkhtmltox_0.12.6-1.focal_amd64.deb

COPY . /code/

# CMD sh -c "/wait && compose/start_gunicorn.sh"
CMD [ "python3", "manage.py", "runserver" ]
