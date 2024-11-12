from database.models import User, Document, Experiment
from sqladmin import ModelView

class UserAdmin(ModelView, model=User):
    column_searchable_list = [User.name]
    column_list = [User.name, User.email, User.created_at]

class DataAdmin(ModelView, model=Document):
    column_list = [Document.id, Document.title, Document.data]

class ExperimentAdmin(ModelView, model=Experiment):
    column_list = [Experiment.name, Experiment.description, "owner.name", Experiment.status]
    column_labels = {"owner.name": "Owner"}
    form_ajax_refs = {
        "owner": {
            "fields": ("name",),
            "order_by": "name",
        }
    }
