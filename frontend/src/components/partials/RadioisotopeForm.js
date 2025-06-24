import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Form from "./Form";
import ButtonGroup from "./ButtonGroup";
import ErrorCard from "./ErrorCard";

import InputText from "./Input/InputText";
import InputNumber from "./Input/InputNumber";

import api from "../../api";

const RadioisotopeForm = (props) => {
  const { radioisotope } = props;

  const [name, setName] = useState(radioisotope ? radioisotope.name : "");
  const [description, setDescription] = useState(
    radioisotope ? radioisotope.description : ""
  );
  const [activity, setActivity] = useState(
    radioisotope ? radioisotope.activity : ""
  );
  const [halflife, setHalflife] = useState(
    radioisotope ? radioisotope.halflife : ""
  );

  const [error, setError] = useState("");
  const [nameError, setNameError] = useState("");
  const [descriptionError, setDescriptionError] = useState("");
  const [activityError, setActivityError] = useState("");
  const [halflifeError, setHalflifeError] = useState("");

  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const resetErrors = () => {
    setError("");
    setNameError("");
    setDescriptionError("");
    setActivityError("");
    setHalflifeError("");
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

    if (!activity) {
      setActivityError("Activity cannot be blank.");
      anyError = true;
    }

    if (!halflife) {
      setHalflifeError("Halflife cannot be blank.");
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
      activity,
      halflife,
    };

    try {
      const endpoint = radioisotope
        ? `/radioisotopes/${radioisotope.id}/edit`
        : "/radioisotopes/new";
      const method = radioisotope ? "patch" : "post";

      const response = await api[method](endpoint, formDetails);

      if (response.status !== 200) {
        setError(response.data.detail || "An error occurred!");
      } else {
        navigate(
          radioisotope ? `/radioisotopes/${radioisotope.id}` : "/radioisotopes"
        );
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
      <InputNumber
        name="activity"
        value={activity}
        setValue={setActivity}
        error={activityError}
        required
      />
      <InputNumber
        name="halflife"
        value={halflife}
        setValue={setHalflife}
        error={halflifeError}
        required
      />
      <ButtonGroup>
        <a
          href={
            radioisotope
              ? `/radioisotopes/${radioisotope.id}`
              : "/radioisotopes"
          }
        >
          Cancel
        </a>
        <button type="submit" disabled={loading} className="btn-primary">
          Save
        </button>
      </ButtonGroup>
    </Form>
  );
};

export default RadioisotopeForm;
