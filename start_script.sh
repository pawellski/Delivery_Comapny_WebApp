#!/bin/bash

mkdir PPD_app/waybill_files
mkdir PPD_app/waybill_images

a="LOGIN_JWT_SECRET=" 
b=$(openssl rand -base64 32)
touch .env
echo "${a}${b}" > .env

