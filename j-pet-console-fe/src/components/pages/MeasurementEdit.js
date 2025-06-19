import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";

import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import MeasurementForm from "../partials/MeasurementForm";

import api from "../../api";

const MeasurementEdit = () => {
  const navigate = useNavigate();
  const { measurement_id } = useParams();

  const [measurement, setMeasurement] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMeasurement = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/measurements/${measurement_id}`);
      setMeasurement(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate("/");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, [measurement_id, navigate]);

  useEffect(() => {
    fetchMeasurement();
  }, [fetchMeasurement]);

  return (
    <Page>
      <ButtonBack path={`/experiments/${measurement.experiment_id}`}>
        Back to the experiment
      </ButtonBack>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchMeasurement} />
      ) : (
        <>
          <h1>Edit measurement - {measurement.name}</h1>
          <MeasurementForm measurement={measurement} />
        </>
      )}
    </Page>
  );
};

export default MeasurementEdit;
