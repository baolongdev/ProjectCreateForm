FROM python:3.8.0
EXPOSE 8501

# Update pip and upgrade it
RUN python3 -m pip install --upgrade pip

WORKDIR /app

# Create a virtual environment
RUN python -m venv venv

# Upgrade pip within the virtual environment
RUN venv/bin/python -m python3 -m pip install --upgrade pip

# Copy your requirements file
COPY requirements.txt /app/

# Install requirements using the virtual environment's Python
RUN venv/bin/python -m pip install -r /app/requirements.txt

# Copy your application files into the container
COPY . .

# Run your Streamlit application using the virtual environment's Python
CMD venv/bin/python -m streamlit run --server.port 8501 --server.enableCORS false app.py
