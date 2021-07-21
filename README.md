# Ensembl Metadata Registry

[![Build Status](https://travis-ci.com/Ensembl/ensembl-metadata-admin.svg?branch=master)](https://travis-ci.com/Ensembl/ensembl-metadata-admin)

Django ORM and admin layer for the Ensembl Metadata database.

## System Requirements

- Python 3.8+
- MySQL Client

## Usage

Clone the repository:
```
git clone -b master https://github.com/Ensembl/ensembl-metadata-admin.git
```

Install the environment (with pyenv)

```
cd ensembl-metadata-admin
pyenv virtualenv 3.8 ensembl_metadata_admin
pyenv local ensembl_metadata_admin
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
export DJANGO_SETTINGS_MODULE=metadata_registry.settings.standard
```

Run the migrate step, for a pre-existing database
```
./manage.py migrate --fake-initial
```

Start the development server
```
 ./manage.py runserver 0:9000
```

Check in the browser
```
http://localhost:9000/
```
