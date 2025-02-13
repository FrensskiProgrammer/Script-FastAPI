from app.models.category import Category
from app.models.products import Product
from sqlalchemy.schema import CreateTable

print(CreateTable(Category.__table__))
print(CreateTable(Product.__table__))