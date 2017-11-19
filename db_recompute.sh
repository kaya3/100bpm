#!/bin/bash

rm app.db
rm -r db_repository/
./db_create.py
./m3u_to_json.py AudioHackWav.m3u 

