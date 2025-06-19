import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";

import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import ExperimentForm from "../partials/ExperimentForm";

import api from "../../api";

const ExperimentEdit = () => {
  const navigate = useNavigate();
  const { experiment_id } = useParams();

  const [experiment, setExperiment] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchExperiment = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/experiments/${experiment_id}`);
      setExperiment(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate("/");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, [experiment_id, navigate]);

  useEffect(() => {
    fetchExperiment();
  }, [fetchExperiment]);

  return (
    <Page>
      <ButtonBack path={`/experiments/${experiment.id}`}>
        Back to the experiment
      </ButtonBack>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchExperiment} />
      ) : (
        <>
          <h1>Edit experiment - {experiment.name}</h1>
          <ExperimentForm experiment={experiment} />
        </>
      )}
    </Page>
  );
};

export default ExperimentEdit;
