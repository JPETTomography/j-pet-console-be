from sqladmin import ModelView

from database.models import (
    DataEntry,
    Detector,
    Experiment,
    Measurement,
    MeasurementDirectory,
    MeteoReadout,
    Radioisotope,
    Tag,
    User,
)


class UserAdmin(ModelView, model=User):
    column_searchable_list = [User.name]
    column_list = [User.name, User.email, User.created_at]


class DetectorAdmin(ModelView, model=Detector):
    column_searchable_list = [Detector.name]
    column_list = [Detector.name, Detector.status, Detector.agent_code]


class ExperimentAdmin(ModelView, model=Experiment):
    column_list = [
        Experiment.name,
        Experiment.description,
        Experiment.status,
        "coordinator.name",
        "detector.name",
    ]
    column_labels = {
        "coordinator.name": "Coordinator",
        "detector.name": "Detector",
    }
    form_ajax_refs = {
        "coordinator": {
            "fields": ("name",),
            "order_by": "name",
        },
        "detector": {
            "fields": ("name",),
            "order_by": "name",
        },
    }


class TagAdmin(ModelView, model=Tag):
    column_searchable_list = [Tag.name]
    column_list = [Tag.name, Tag.description]


class RadioisotopeAdmin(ModelView, model=Radioisotope):
    column_searchable_list = [Radioisotope.name]
    column_list = [
        Radioisotope.name,
        Radioisotope.description,
        Radioisotope.activity,
        Radioisotope.halflife,
    ]


class MeasurementAdmin(ModelView, model=Measurement):
    column_searchable_list = [Measurement.name]
    column_list = [
        Measurement.name,
        Measurement.description,
        "experiment.name",
    ]
    column_labels = {"experiment.name": "Experiment"}
    form_ajax_refs = {
        "experiment": {
            "fields": ("name",),
            "order_by": "name",
        },
    }


class DataEntryAdmin(ModelView, model=DataEntry):
    column_searchable_list = [DataEntry.name]
    column_list = [
        DataEntry.name,
        DataEntry.acquisition_date,
        DataEntry.data,
        DataEntry.measurement_id,
    ]


class MeteoReadoutAdmin(ModelView, model=MeteoReadout):
    column_searchable_list = [
        MeteoReadout.station_time,
        MeteoReadout.agent_time,
    ]
    column_list = [
        MeteoReadout.station_time,
        MeteoReadout.agent_time,
        "measurement.name",
    ]
    column_labels = {"measurement.name": "Measurement"}
    form_ajax_refs = {
        "measurement": {
            "fields": ("name",),
            "order_by": "name",
        },
    }


class MeasurementDirectoryAdmin(ModelView, model=MeasurementDirectory):
    column_searchable_list = [
        MeasurementDirectory.path,
        MeasurementDirectory.created_at,
        MeasurementDirectory.available,
        MeasurementDirectory.experiment_id,
    ]
    column_list = [
        MeasurementDirectory.path,
        MeasurementDirectory.created_at,
        MeasurementDirectory.available,
        MeasurementDirectory.experiment_id,
        "experiment.name",
    ]

    column_labels = {"experiment.name": "Experiment"}
    form_ajax_refs = {
        "experiment": {
            "fields": ("name",),
            "order_by": "name",
        },
    }
