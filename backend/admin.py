from database.models import User, Detector, Experiment, Tag, Document
from sqladmin import ModelView

class UserAdmin(ModelView, model=User):
    column_searchable_list = [User.name]
    column_list = [User.name, User.email, User.created_at]

class DetectorAdmin(ModelView, model=Detector):
    column_searchable_list = [Detector.name]
    column_list = [Detector.name, Detector.status, Detector.agent_ip]

class ExperimentAdmin(ModelView, model=Experiment):
    column_list = [Experiment.name, Experiment.description, Experiment.status, "coordinator.name", "detector.name"]
    column_labels = {"coordinator.name": "Coordinator", "detector.name": "Detector"}
    form_ajax_refs = {
        "coordinator": {
            "fields": ("name",),
            "order_by": "name",
        },
        "detector": {
            "fields": ("name",),
            "order_by": "name",
        }
    }

class TagAdmin(ModelView, model=Tag):
    column_searchable_list = [Tag.name]
    column_list = [Tag.name, Tag.description]

class DataAdmin(ModelView, model=Document):
    column_list = [Document.id, Document.title, Document.data]
