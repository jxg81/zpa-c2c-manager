#!/usr/bin/env bash

DIR="./package"
PACKAGE_NAME="lambda_package.zip"


if [ ! -d "$DIR" ]; then
  mkdir package
fi

if [ -f "$PACKAGE_NAME" ]; then
  rm $PACKAGE_NAME
fi

pip install --target ./package pyzscaler

cd package
zip -r ../$PACKAGE_NAME .

cd ..
zip $PACKAGE_NAME *.py

