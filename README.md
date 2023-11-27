
# SotisImmo_ETL: Real Estate Data Extraction Tool

## Overview
SotisImmo_ETL is designed for scraping and processing real estate data. It offers functionality to extract data from various online sources, clean and normalize the data, and store it in a SQL database.

## Prerequisites
- Anaconda or Miniconda
- Docker (for Docker deployment)

## Installation and Setup

### Running without Docker

1. **Clone the Repository and Navigate to Directory**
    ```bash
    cd [your-folder-path]/SotisImmo_ETL
    ```

2. **Environment Setup**
    - Activate the Conda environment:
        ```bash
        conda activate myenv
        ```

3. **Start the ETL Process**
    - Run the Python script:
        ```bash
        python main.py
        ```

4. **Configuration**
    - Using `modules/config.py`, configure the scraping parameters:
        - Year (e.g., `2023`)
        - [Optional] Department (default: `1`)

    - Example: Selecting `2023` and `1` will iterate over all departments (from 1 to 914) for the year 2023.

5. **Process**
    - Iterates over each department (1 to 95) from `onset_date` to `offset_date`.
    - Fetches and parses online data for offers.
    - Cleans, normalizes, and stores data in the SQL database.

### Running with Docker

1. **Prepare Docker Environment**
    - Ensure Docker is installed and running on your system.

2. **Navigate to Project Directory**
    ```bash
    cd [your-folder-path]/SotisImmo_ETL
    ```

3. **Build and Start the Container**
    ```bash
    docker-compose up --build
    ```

    - Note: If you encounter issues with `pymssql`, adjust its version in `requirements.txt` or remove it before building the Docker image.

## Additional Notes
- Modify `requirements.txt` as needed for compatibility with your environment.
