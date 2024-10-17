from models import User
from sqladmin import ModelView

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email, User.created_at]
