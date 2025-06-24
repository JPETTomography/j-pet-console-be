import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import DetectorCard from "../partials/DetectorCard";

import Page from "../partials/Page";
import PaginatedItems from "../partials/PaginatedItems";
import ButtonNew from "../partials/ButtonNew";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import api from "../../api";

const DetectorsList = () => {
  const navigate = useNavigate();

  const [detectors, setDetectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDetectors = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get("/detectors");
      setDetectors(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate("/");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchDetectors();
  }, [fetchDetectors]);

  return (
    <Page>
      <h1>Detectors List</h1>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchDetectors} />
      ) : (
        <PaginatedItems
          items={detectors}
          ItemComponent={DetectorCard}
          newButton={
            <ButtonNew path="/detectors/new">Add new detector</ButtonNew>
          }
        />
      )}
    </Page>
  );
};

export default DetectorsList;
