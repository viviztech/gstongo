#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run tests
echo "Running Backend Tests..."
python manage.py test apps.users apps.gst_filing apps.invoices apps.franchise --settings=gstongo.settings_test

# Deactivate
deactivate
