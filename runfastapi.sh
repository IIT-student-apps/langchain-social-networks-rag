#!/bin/bash
source venv/bin/activate
cd api
uvicorn main:app --reload
