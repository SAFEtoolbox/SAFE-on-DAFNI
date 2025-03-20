# Use the official Python 3.8 image from Dockerhub to provide a Python environment
FROM python:3.8

# copy and install requirements 
COPY requirements.txt .
RUN pip install --no-cache-dir --compile -r requirements.txt

RUN mkdir -p /data/inputs/
RUN mkdir -p /data/outputs/

# Copy the contents from the local directory to the output container's directory
COPY run.py .
COPY util.py .
COPY HyMod.py .


# Tell Docker how to run the Model when it starts the container. 
CMD ["python", "run.py"]
