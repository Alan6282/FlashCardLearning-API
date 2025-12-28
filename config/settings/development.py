from .base import * 
from dotenv import load_dotenv

# Development
DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS=[] # Keeping this empty will take this by default: ['localhost', '127.0.0.1']



os.makedirs(LOGS_DIR, exist_ok=True) 

LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['handlers']['file']['level'] = 'DEBUG'
LOGGING['handlers']['file']['filename'] = os.path.join(LOGS_DIR, 'dev.log')

for logger in LOGGING['loggers'].values():
    logger['level'] = 'DEBUG'

LOGGING['loggers']['django']['level'] = 'WARNING'