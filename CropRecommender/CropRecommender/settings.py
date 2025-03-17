from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

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
    'Homepage', #main page
    'compressor',#static file minimizer app @KEYO
    'agriBot',
    'Social',# For user socialization

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

TIME_ZONE = 'UTC'

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

# KEYO 11
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


