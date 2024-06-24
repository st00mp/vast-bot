#!/bin/bash

# This script runs any necessary initialization tasks before starting the main application.

# Exit immediately if a command exits with a non-zero status.
set -e

# Print all executed commands to the terminal.
set -x

# Run database migrations (if any)
# flask db upgrade

# Any other initialization tasks can go here

# Finally, run the main application
exec "$@"
