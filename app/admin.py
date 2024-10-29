from models import User, Experiment
from sqladmin import ModelView

class UserAdmin(ModelView, model=User):
    column_searchable_list = [User.name]
    column_list = [User.name, User.email, User.created_at]
    column_details_exclude_list = [User.experiments]
    form_excluded_columns = [User.experiments]

class ExperimentAdmin(ModelView, model=Experiment):
    column_list = [Experiment.name, Experiment.description, "owner.name", Experiment.status]
    column_labels = {"owner.name": "Owner"}
    form_ajax_refs = {
        "owner": {
            "fields": ("name",),
            "order_by": "name",
        }
    }