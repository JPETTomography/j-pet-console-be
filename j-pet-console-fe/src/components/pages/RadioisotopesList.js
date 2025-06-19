import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import RadioisotopeCard from "../partials/RadioisotopeCard";

import Page from "../partials/Page";
import PaginatedItems from "../partials/PaginatedItems";
import ButtonNew from "../partials/ButtonNew";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import api from "../../api";

const RadioisotopesList = () => {
  const navigate = useNavigate();


  const [radioisotopes, setRadioisotopes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRadioisotopes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get("/radioisotopes");
      setRadioisotopes(response.data);
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
    fetchRadioisotopes();
  }, [fetchRadioisotopes]);

  return (
    <Page>
      <h1>Radioisotopes List</h1>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchRadioisotopes} />
      ) : (
        <PaginatedItems
          items={radioisotopes}
          ItemComponent={RadioisotopeCard}
          newButton={
            <ButtonNew path="/radioisotopes/new">
              Add new radioisotope
            </ButtonNew>
          }
        />
      )}
    </Page>
  );
};

export default RadioisotopesList;
