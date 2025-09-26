import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import ExperimentCard from "../partials/ExperimentCard";

import Page from "../partials/Page";
import PaginatedItems from "../partials/PaginatedItems";
import ButtonNew from "../partials/ButtonNew";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import api from "../../api";
import { usePermissions } from "../../hooks/usePermissions";

const ExperimentsList = () => {
  const navigate = useNavigate();
  const { canManageExperiments } = usePermissions(); // Optimized permission check

  const [experiments, setExperiments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchExperiments = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get("/experiments");
      setExperiments(response.data);
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
    fetchExperiments();
  }, [fetchExperiments]);

  return (
    <Page>
      <h1>Experiments List</h1>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchExperiments} />
      ) : (
        <PaginatedItems
          items={experiments}
          ItemComponent={ExperimentCard}
          newButton={
            canManageExperiments ? (
              <ButtonNew path="/experiments/new">Add new experiment</ButtonNew>
            ) : null
          }
        />
      )}
    </Page>
  );
};

export default ExperimentsList;
