# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory to /pokefetch
WORKDIR /pokefetch

# Copy the current directory contents into the container at /pokefetch
COPY . /pokefetch

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Expose the port for the Prometheus metrics endpoint
EXPOSE 8000

# Run pokefetch.py when the container launches
CMD ["python", "pokefetch_src/pokefetch.py"]
