from database.models import User, Document
from sqladmin import ModelView

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email, User.created_at]

class DataAdmin(ModelView, model=Document):
    column_list = [Document.id, Document.title, Document.data]
