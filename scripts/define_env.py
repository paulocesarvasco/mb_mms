import os
from getpass import getpass

def prompt_user():
    defaults = {
        "DB_USER": "mysql",
        "DB_PASSWORD": "mysql",
        "DB_HOST": "localhost",
        "PAIRS": "BRLBTC,BRLETH",
    }

    print("Please provide the following details for the .env file (press Enter to use defaults):")

    db_user = input(f"DB_USER (default: {defaults['DB_USER']}): ") or defaults["DB_USER"]
    db_password = getpass(f"DB_PASSWORD (default: {defaults['DB_PASSWORD']}): ") or defaults["DB_PASSWORD"]
    db_host = input(f"DB_HOST (default: {defaults['DB_HOST']}): ") or defaults["DB_HOST"]

    db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/mb"

    pairs = input(f"PAIRS (default: {defaults['PAIRS']}): ") or defaults["PAIRS"]

    mb_api = 'https://mobile.mercadobitcoin.com.br/v4/{}/candle?from={}&to={}&precision=1d'

    env_content = f"""DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST={db_host}
DB_DATABASE=mb

MB_API={mb_api}
DB_URL={db_url}

PAIRS={pairs}
"""

    env_path = os.path.join(os.path.dirname(os.getcwd()), ".env")
    with open(env_path, "w") as env_file:
        env_file.write(env_content)

    print(f".env file has been created at: {env_path}")

if __name__ == "__main__":
    prompt_user()
