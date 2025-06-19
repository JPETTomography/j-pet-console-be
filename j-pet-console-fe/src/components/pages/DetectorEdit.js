import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";
import api from "../../api";

import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import DetectorForm from "../partials/DetectorForm";

const DetectorEdit = () => {
  const navigate = useNavigate();

  const { detector_id } = useParams();

  const [detector, setDetector] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDetector = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/detectors/${detector_id}`);
      setDetector(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate("/");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, [detector_id, navigate]);

  useEffect(() => {
    fetchDetector();
  }, [fetchDetector, detector_id]);

  return (
    <Page>
      <ButtonBack path={`/detectors/${detector.id}`}>
        Back to the detector
      </ButtonBack>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchDetector} />
      ) : (
        <>
          <h1>Edit detector - {detector.name}</h1>
          <DetectorForm detector={detector} />
        </>
      )}
    </Page>
  );
};

export default DetectorEdit;
