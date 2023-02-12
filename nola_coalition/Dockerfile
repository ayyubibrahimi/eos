# As Scrapy runs on Python, I choose the official Python 3 Docker image.
FROM python:3
 
WORKDIR /opt/nolaco
 
COPY requirements.txt ./
 
RUN pip3 install --no-cache-dir -r requirements.txt
 
# Copy the project source code from the local host to the filesystem of the container at the working directory.
COPY monitor.py .
 
# Run the crawler when the container launches.
CMD [ "python3", "monitor.py" ]