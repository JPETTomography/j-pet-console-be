import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import Form from "./Form";
import ButtonGroup from "./ButtonGroup";
import ErrorCard from "./ErrorCard";

import InputText from "./Input/InputText";
import InputSelect from "./Input/InputSelect";
import InputDate from "./Input/InputDate";

import api from "../../api";

const ExperimentForm = (props) => {
  const { experiment } = props;

  const [coordinators, setCoordinators] = useState([]);
  const [detectors, setDetectors] = useState([]);

  const [name, setName] = useState(experiment ? experiment.name : "");
  const [description, setDescription] = useState(
    experiment ? experiment.description : ""
  );
  const [status, setStatus] = useState(experiment ? experiment.status : "");
  const [location, setLocation] = useState(
    experiment ? experiment.location : ""
  );
  const [startDate, setStartDate] = useState(
    experiment ? experiment.start_date : ""
  );
  const [endDate, setEndDate] = useState(
    experiment ? experiment.end_date || "" : ""
  );
  const [coordinatorId, setCoordinatorId] = useState(
    experiment ? experiment.coordinator_id : ""
  );
  const [detectorId, setDetectorId] = useState(
    experiment ? experiment.detector_id : ""
  );

  const [error, setError] = useState("");
  const [nameError, setNameError] = useState("");
  const [descriptionError, setDescriptionError] = useState("");
  const [statusError, setStatusError] = useState("");
  const [locationError, setLocationError] = useState("");
  const [startDateError, setStartDateError] = useState("");
  const [endDateError, setEndDateError] = useState("");
  const [coordinatorIdError, setCoordinatorIdError] = useState("");
  const [detectorIdError, setDetectorIdError] = useState("");

  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const fetchCoordinators = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get("/users?role=coordinator");
      const data = response.data;
      if (!experiment) data.unshift({ id: "", name: "-" });
      setCoordinators(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, [experiment]);

  const fetchDetectors = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get("/detectors");
      const data = response.data;
      if (!experiment) data.unshift({ id: "", name: "-" });
      setDetectors(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, [experiment]);

  useEffect(() => {
    fetchCoordinators();
    fetchDetectors();
  }, [fetchCoordinators, fetchDetectors]);

  const resetErrors = () => {
    setError("");
    setNameError("");
    setDescriptionError("");
    setStatusError("");
    setLocationError("");
    setStartDateError("");
    setEndDateError("");
    setCoordinatorIdError("");
    setDetectorIdError("");
  };

  const validateForm = () => {
    let anyError = false;

    if (!name) {
      setNameError("Name cannot be blank.");
      anyError = true;
    }

    if (!description) {
      setDescriptionError("Description cannot be blank.");
      anyError = true;
    }

    if (!status) {
      setStatusError("Status cannot be blank.");
      anyError = true;
    }

    if (!location) {
      setLocationError("Location cannot be blank.");
      anyError = true;
    }

    if (!startDate) {
      setStartDateError("Start date cannot be blank.");
      anyError = true;
    }

    if (startDate && endDate && endDate < startDate) {
      setEndDateError("End date must be after start date.");
      anyError = true;
    }

    if (!coordinatorId) {
      setCoordinatorIdError("Coordinator cannot be blank.");
      anyError = true;
    }

    if (!detectorId) {
      setDetectorIdError("Detector cannot be blank.");
      anyError = true;
    }

    if (anyError) return false;

    resetErrors();
    return true;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    resetErrors();
    if (!validateForm()) return;
    setLoading(true);

    const formDetails = {
      name,
      description,
      status,
      location,
      start_date: startDate,
      end_date: endDate,
      coordinator_id: coordinatorId,
      detector_id: detectorId,
    };

    try {
      const endpoint = experiment
        ? `/experiments/${experiment.id}/edit`
        : "/experiments/new";
      const method = experiment ? "patch" : "post";

      const response = await api[method](endpoint, formDetails);

      if (response.status !== 200) {
        setError(response.data.detail || "An error occurred!");
      } else {
        navigate(experiment ? `/experiments/${experiment.id}` : "/experiments");
      }
    } catch (err) {
      const errorDetail = err.response?.data?.detail;
      if (Array.isArray(errorDetail)) {
        const formattedErrors = errorDetail
          .map((item) => item.msg + ": " + item.loc[1] + ".")
          .join("\n");
        setError(formattedErrors);
      } else {
        setError(err.message || "An unknown error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      {error && <ErrorCard>{error}</ErrorCard>}
      <InputText
        name="name"
        value={name}
        setValue={setName}
        error={nameError}
        required
      />
      <InputText
        name="description"
        value={description}
        setValue={setDescription}
        error={descriptionError}
        required
      />
      <InputSelect
        name="status"
        value={status}
        setValue={setStatus}
        error={statusError}
        selectOptions={[
          { value: "", label: "-" },
          { value: "draft", label: "Draft" },
          { value: "ongoing", label: "Ongoing" },
          { value: "closed", label: "Closed" },
          { value: "archived", label: "Archived" },
        ]}
        required
      />
      <InputText
        name="location"
        value={location}
        setValue={setLocation}
        error={locationError}
        required
      />
      <InputDate
        name="start date"
        value={startDate}
        setValue={setStartDate}
        error={startDateError}
        required
      />
      <InputDate
        name="end date"
        value={endDate}
        setValue={setEndDate}
        error={endDateError}
      />
      <InputSelect
        name="coordinator"
        value={coordinatorId}
        setValue={setCoordinatorId}
        error={coordinatorIdError}
        selectOptions={coordinators.map((coordinator) => {
          return { value: coordinator.id, label: coordinator.name };
        })}
        required
      />
      <InputSelect
        name="detector"
        value={detectorId}
        setValue={setDetectorId}
        error={detectorIdError}
        selectOptions={detectors.map((detector) => {
          return { value: detector.id, label: detector.name };
        })}
        required
      />
      <ButtonGroup>
        <a href={experiment ? `/experiments/${experiment.id}` : "/experiments"}>
          Cancel
        </a>
        <button type="submit" disabled={loading} className="btn-primary">
          Save
        </button>
      </ButtonGroup>
    </Form>
  );
};

export default ExperimentForm;
