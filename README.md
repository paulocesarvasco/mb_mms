# Moving Average API

## Overview
This is a Python 3.13 application that calculates and stores moving averages for cryptocurrency assets. The asset data is retrieved from the public API of Mercado Bitcoin, and the computed moving averages are stored in a MariaDB database. The application is built using Flask and runs on Gunicorn as the web server.

## Features
- Retrieves cryptocurrency asset data from the Mercado Bitcoin public API.
- Computes moving averages and stores them in a MariaDB database.
- Provides an API to access the stored moving averages.
- Uses SQLAlchemy for database interaction.
- Includes CLI commands for database initialization and data population.
- Implements a job scheduler (APScheduler) to insert daily moving averages.

## Technologies Used
- **Python 3.13**
- **Poetry** for dependency management
- **Flask** as the web framework
- **Gunicorn** as the web server
- **MariaDB** as the database
- **SQLAlchemy** for ORM and database interaction
- **APScheduler** for scheduled tasks

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.13
- Poetry
- MariaDB

### Setup
1. Clone the repository:
   ```sh
   git git@github.com:paulocesarvasco/mb_mms.git
   cd mb_mms
   ```
2. Install dependencies using Poetry:
   ```sh
   poetry install
   ```

## Usage
### Initialize the Database
To create the required table in the MariaDB database, run:
```sh
poetry run flask --app mb_mms init-db
```

### Populate Database with Historical Data
To fetch and store moving average data for the last 365 days, execute:
```sh
poetry run flask --app mb_mms populate-db
```

### Start the Application

#### Production mode

To run the application using Gunicorn:
```sh
poetry run gunicorn -w 4 -b 0.0.0.0:8000 "mb_mms.wsgi:app"
```

#### Development mode
To configure the environment execute:
```sh
poetry run python scripts/define_env.py
```

To run the application using Flask:
```sh
poetry run flask --app mb_mms run
```

### Scheduled Jobs
The APScheduler automatically inserts daily moving averages into the database.

## API Endpoints
- `GET /v1/<pair>/mms?from=<timestamp>&to=<timestamp>&precision=<interval>`
  - **Path Parameter:**
    - `pair`: Cryptocurrency pair (e.g., BRLBTC, BRLETH)
  - **Query Parameters:**
    - `from`: Start timestamp (e.g., 1577836800)
    - `to`: End timestamp (e.g., 1606565306)
    - `precision`: Moving average interval (e.g., 20d)

## Moving Average Calculation
To populate the database, a function retrieves historical data from the last 365 days. A sliding window approach is used with window sizes of 20, 50, and 200 to compute moving averages over all records.

From a persistence perspective, a database session is created, and each computed value is inserted. At the end of the process, all operations are committed in a single transaction for efficiency.

## Development Status
Currently, the application only runs locally and is still in progress. A containerized version will be available soon.

## License
This project is licensed under the MIT License.
