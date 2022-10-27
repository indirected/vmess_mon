#!/bin/bash

# check if docker is installed
if ! command -v docker &> /dev/null
then
    echo "docker could not be found, you should install docker first"
    exit
fi

# check if docker-compose is installed
if ! command -v docker-compose &> /dev/null
then
    echo "docker-compose could not be found, you should install docker-compose first"
    exit
fi


# check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "pip could not be found, you should install pip first"
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

