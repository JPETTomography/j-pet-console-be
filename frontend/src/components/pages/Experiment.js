import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";

import { formatDate } from "../../utils/formatDate";

import Svg from "../partials/Svg";

import Badge from "../partials/Badge";
import ButtonGroup from "../partials/ButtonGroup";
import ButtonBack from "../partials/ButtonBack";
import ButtonEdit from "../partials/ButtonEdit";

import Page from "../partials/Page";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import MeasurementsList from "../partials/MeasurementsList";
import api from "../../api";

const Experiment = () => {
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
  }, [fetchExperiment, experiment_id]);

  return (
    <Page>
      <ButtonBack path={"/experiments"}>Back to experiments list</ButtonBack>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchExperiment} />
      ) : (
        <>
          <div className="grid grid-cols-[1fr_400px] gap-8">
            <MeasurementsList />
            <div className="flex flex-col gap-6">
              <div className="flex justify-between items-start gap-4">
                <h2>{experiment.name}</h2>
                <div className="flex gap-4">
                  <Badge status={experiment.status} />
                </div>
              </div>
              <p className="text-xl">{experiment.description}</p>
              <div className="flex flex-col gap-2">
                <div className="shrink-0 flex items-center gap-2 mb-auto text-sm">
                  <Svg src="/icons/calendar-days.svg" className="w-6 h-6" />
                  <span>
                    {formatDate(experiment.start_date)} -{" "}
                    {experiment.end_date
                      ? formatDate(experiment.end_date)
                      : "..."}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Svg src="/icons/map-pin.svg" className="w-6 h-6" />
                  {experiment.location}
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Svg src="/icons/user-circle.svg" className="w-6 h-6" />
                  {experiment.coordinator.name}
                </div>
              </div>
              <ButtonGroup>
                <ButtonEdit path={`/experiments/${experiment.id}/edit`} />
              </ButtonGroup>
            </div>
          </div>
        </>
      )}
    </Page>
  );
};

export default Experiment;
