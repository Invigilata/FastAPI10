from app.backend.db import Base, engine
from app.models import User, Task

# Создаём все таблицы
Base.metadata.create_all(bind=engine)

# Для вывода SQL-запросов создания таблиц
from sqlalchemy import Table
from sqlalchemy.schema import CreateTable

for table in Base.metadata.sorted_tables:
    print(CreateTable(table).compile(engine))
