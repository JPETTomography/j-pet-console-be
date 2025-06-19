import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";

import Svg from "../partials/Svg";

import Badge from "../partials/Badge";
import ButtonBack from "../partials/ButtonBack";
import ButtonEdit from "../partials/ButtonEdit";

import Page from "../partials/Page";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";

import api from "../../api";

const Detector = () => {
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
      <ButtonBack path={"/detectors"}>Back to detectors list</ButtonBack>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchDetector} />
      ) : (
        <>
          <div className="flex flex-col gap-2">
            <div className="flex justify-between items-center gap-4">
              <h1>{detector.name}</h1>
              <div className="flex gap-4">
                <Badge status={detector.status} />
              </div>
            </div>
            <div className="grid grid-cols-1 gap-4 pt-2">
              <p className="text-xl">{detector.description}</p>
              <div className="flex items-center gap-2 text-sm">
                <Svg src="/icons/globe-europe-africa.svg" className="w-6 h-6" />
                {detector.agent_code}
              </div>
              <ButtonEdit path={`/detectors/${detector.id}/edit`} />
            </div>
          </div>
        </>
      )}
    </Page>
  );
};

export default Detector;
