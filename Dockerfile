FROM python:3.7.2

# Create app directory
ADD app.py /

# Install app dependencies
COPY requirements.txt ./

# run the requirements.txt file
RUN pip install -r requirements.txt

EXPOSE 8080
CMD [ "python", "./app.py" ]