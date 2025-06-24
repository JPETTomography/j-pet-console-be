import { useState, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";

import MeasurementCard from "../partials/MeasurementCard";

import PaginatedItems from "../partials/PaginatedItems";
import ButtonNew from "../partials/ButtonNew";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import api from "../../api";

const MeasurementsList = () => {
  const { experiment_id } = useParams();
  const navigate = useNavigate();

  const [measurements, setMeasurements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMeasurements = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(
        `/experiments/${experiment_id}/measurements`
      );
      setMeasurements(response.data);
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
    fetchMeasurements();
  }, [fetchMeasurements]);

  return (
    <div className="flex-1 flex flex-col gap-8">
      <h1>Measurements List</h1>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchMeasurements} />
      ) : (
        <PaginatedItems
          items={measurements}
          ItemComponent={MeasurementCard}
          newButton={
            <ButtonNew path={`/experiments/${experiment_id}/measurements/new`}>
              Add new measurement
            </ButtonNew>
          }
        />
      )}
    </div>
  );
};

export default MeasurementsList;