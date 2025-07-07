#!/bin/bash
alembic revision --autogenerate -m "create devices table"
alembic upgrade head
python main.py
