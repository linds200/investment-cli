database_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password':'MaxyMoo123!',
    'database': 'investment_cli_db'
}
class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{database_config.get('user')}:{database_config.get('password')}@{database_config.get('host')}:{database_config.get('port')}/{database_config.get('database')}"