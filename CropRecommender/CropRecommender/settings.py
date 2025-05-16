from pathlib import Path
# Imports for google cloud storage
import os
from google.oauth2 import service_account
from dotenv import load_dotenv#for loading the environment variables from .env file

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv()

# # Retrieve Google Maps API key
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-78yh0vxpsgpsu=#*4^#i3wf!qnzufuq!vnw$5g!d^w!#h$o#op'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True#Planning  to deploy changed from tru to false @KEYO I***f i will deploy i should change it to false**

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages', #for google cloud storage
    'Homepage', #main page
    'compressor',#static file minimizer app @KEYO
    'agriBot',
    'Social',# For user socialization
    'resource', #Resource Hub
    'market', #Farmer market place
    'forecast', #for app forecasting
    'widget_tweaks', #form customization pip installed
    

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',#allows static files to run even when debug is set to true
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage" #FEB Temporary for automatic updates
WHITENOISE_AUTOREFRESH = True #Feb Keyo

ROOT_URLCONF = 'CropRecommender.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR /'templates'], #Keyo square brackets to specify templating is global
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'CropRecommender.context_processors.google_maps_api_key', #captures the googleMaps API Key by loading it from cotextProcessors file that was created
            ],
        },
    },
]

WSGI_APPLICATION = 'CropRecommender.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# postgres database(CropRecommender) details

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'CropRecommender',
        'USER': 'postgres',
        'PASSWORD': 'Azerty@12',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi' #specific timezone to use

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_ROOT = BASE_DIR / 'productionfiles' #KEYO to collect all static files when debug is false
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    ] #KEYO this helps in collecting static files to productionFiles updates with the one set in static file

# @KEYO Compressor Configuration
COMPRESS_ROOT = BASE_DIR / 'static'
# COMPRESS_ENABLED = True #CAUSING UNEXPLAINED PROBLEMS COMMENTED OUT to be safe
# COMPRESS_OFFLINE = True #precompress files before deployment

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",#the first two were added to assist in locating output.css
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    'compressor.finders.CompressorFinder',)

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# KEYO 11 For storing files locally commented since post files are stored in the cloud
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# Keyo 20th storage settings for google cloud storage
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/admin/Downloads/PROJECT/Application/RecommenderSystem/CropRecommender/smart_farmersKey.json" #authenticate user to fetch file
# uploads stored in Google Cloud Storage
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = "smart_farmer"
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, "smart_farmersKey.json")
)
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"

# ADDED BY ME 29/04 This enables caching the GAPs 
# If you will deploy use redis this is just a temporary caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-cache-name',
    }
}

# MPESA CREDENTIALS
MPESA_ENVIRONMENT = 'sandbox'
MPESA_CONSUMER_KEY = 'elMPFU5Cqd63CyNKPEB4nfsjpLXXv2MOPUxDG4EHbDaMXK8f'
MPESA_CONSUMER_SECRET = 'StaruuCkE1wAl3JzAftq80fyGpGyEFNmVVRexjVidr4TfRuQo7A6MH08XD6nKy4O'
MPESA_SHORTCODE = '174379'
MPESA_EXPRESS_SHORTCODE = '174379'
MPESA_SHORTCODE_TYPE = 'paybill'
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
MPESA_INITIATOR_USERNAME = 'testapi'
MPESA_INITIATOR_SECURITY_CREDENTIAL = 'Safaricom123!' 

MPESA_CALLBACK_URL = 'https://8854-154-159-252-189.ngrok-free.app.io/market/mpesa/callback/'





