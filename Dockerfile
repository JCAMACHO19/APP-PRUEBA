FROM python:3.12.5

# Expose the port Streamlit will run on
EXPOSE 8501

# Create the /TAA directory
RUN mkdir -p /APP-PRUEBA

# Set the working directory to /TAA
WORKDIR /APP-PRUEBA

# Copy the requirements.txt file into the /TAA directory
COPY requirements_linux.txt ./requirements_linux.txt
# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements_linux.txt

# Copy all files from the current directory to /TAA, excluding the Documentacion folder
COPY . .

# Set the entry point to run Streamlit
ENTRYPOINT ["streamlit", "run"]

# Set the default command to run the app.py script
CMD ["app.py"]