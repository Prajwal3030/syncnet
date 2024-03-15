# Use Debian as the base image
FROM debian:buster

# Install dependencies required for building Python
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    zlib1g-dev \
    ffmpeg

# Download and install Python 3.5.5
RUN wget https://www.python.org/ftp/python/3.5.5/Python-3.5.5.tgz \
    && tar xvf Python-3.5.5.tgz \
    && cd Python-3.5.5 \
    && ./configure \
    && make \
    && make install

# Create a symbolic link for Python 3.5
RUN ln -s /usr/local/bin/python3.5 /usr/local/bin/python \
    && ln -s /usr/local/bin/pip3.5 /usr/local/bin/pip

# Install pip for Python 3.5
RUN wget https://bootstrap.pypa.io/pip/3.5/get-pip.py \
    && python get-pip.py

# Set up the working directory
WORKDIR /app

# Copy the Flask app and other necessary files into the container
COPY . /app

# Install any Python dependencies
RUN pip install --upgrade pip
RUN pip install Flask

# Expose the port the app runs on
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]
