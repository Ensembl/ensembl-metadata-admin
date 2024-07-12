# Ensembl Metadata Registry

[![Build Status](https://travis-ci.com/Ensembl/ensembl-metadata-admin.svg?branch=master)](https://travis-ci.com/Ensembl/ensembl-metadata-admin)

Django ORM and admin layer for the Ensembl Metadata database.

## System Requirements

- Python 3.8+
- MySQL Client

## Usage

Clone the repository:
```
git clone -b main https://github.com/Ensembl/ensembl-metadata-admin.git
```

Install the environment (with pyenv)

```
cd ensembl-metadata-admin
pyenv local 3.8
pip install --upgrade pip
pip install -r requirements.txt
```

Provide the right credentials to connect to the ensembl-metadata database in secrets.py
```
cd metadata_registry/settings
cp secrets_template.py secrets.py
# Update ensembl_metadata/settings/secrets.py with a SECRET_KEY and database details.
```

Create an environment variable for the settings
```
export DJANGO_SETTINGS_MODULE=metadata_admin.settings
```

Run the migrate step, for a pre-existing database
```
./manage.py migrate --fake-initial
```

Start the development server
```
 ./manage.py runserver
```

Configuration present a sqlite db for the Django related tables `src/django_db`.
Two Backend users
- ensprod / Ensembl : superuser
- ensuser / Ensembl : standard user

Check in the browser
```
http://localhost:8000
```
