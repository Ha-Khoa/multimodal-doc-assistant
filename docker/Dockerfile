#Dockerfile

# Base Image - Python 3.13
FROM python:3.13-slim

# Folder to work inside the container
WORKDIR /multimodal-doc-assistant

#requirements.txt
# copy requirements.txt first so whenever we fix a code, the Docker doesn't need to reinstall all the pip
COPY requirements.txt .

#Set up libraries for python 
RUN pip install --no-cache-dir -r requirements.txt

#Copy everything from the source to the container
COPY . . 

#Expose port Streamlit
EXPOSE 8501

#Run the container
CMD ["streamlit", "run", "app/main.py", "--server.address=0.0.0.0"]