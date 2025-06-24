import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";

import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import RadioisotopeForm from "../partials/RadioisotopeForm";

import api from "../../api";

const RadioisotopeEdit = () => {
  const navigate = useNavigate();
  const { radioisotope_id } = useParams();

  const [radioisotope, setRadioisotope] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRadioisotope = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/radioisotopes/${radioisotope_id}`);
      setRadioisotope(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate("/");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, [radioisotope_id, navigate]);

  useEffect(() => {
    fetchRadioisotope();
  }, [fetchRadioisotope]);

  return (
    <Page>
      <ButtonBack path={`/radioisotopes/${radioisotope.id}`}>
        Back to the radioisotope
      </ButtonBack>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchRadioisotope} />
      ) : (
        <>
          <h1>Edit radioisotope - {radioisotope.name}</h1>
          <RadioisotopeForm radioisotope={radioisotope} />
        </>
      )}
    </Page>
  );
};

export default RadioisotopeEdit;
