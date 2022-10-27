#!/bin/bash

set -e

# check if docker is installed
if ! command -v docker &> /dev/null
then
    echo "docker not found, Install Docker then run again."
    exit
fi

# check if docker-compose is installed
if ! command -v docker-compose &> /dev/null
then
    echo "docker-compose not found, Install docker-compose then run again."
    exit
fi


# check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "pip not found,Install python>= 3.8 and pip then run again."
    exit
fi

# install requirements
python3 -m pip install -r requirements.txt

echo ""
echo ""
echo ""
echo "Plese enter Mongodb database connection string:"
read dbconstring
echo ""
echo "Plese enter discord webhook:"
read discord

# create necessary files
echo $dbconstring > dbconstring
echo $discord > discord

echo "Installed. Run python3 vmessman.py -h for help"
