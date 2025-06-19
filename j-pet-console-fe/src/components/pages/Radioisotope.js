import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";

import Svg from "../partials/Svg";

import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";
import ButtonEdit from "../partials/ButtonEdit";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import api from "../../api";

const Radioisotope = () => {
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
  }, [fetchRadioisotope, radioisotope_id, navigate]);

  return (
    <Page>
      <ButtonBack path="/radioisotopes">Back to radioisotopes list</ButtonBack>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchRadioisotope} />
      ) : (
        <>
          <div className="flex flex-col gap-2">
            <div className="flex justify-between items-center gap-4">
              <h1>{radioisotope.name}</h1>
            </div>
            <div className="grid grid-cols-1 gap-4 pt-2">
              <p className="text-xl">{radioisotope.description}</p>
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="flex items-center gap-2 text-sm">
                  <Svg src="/icons/bolt.svg" className="w-6 h-6" />
                  {radioisotope.activity}
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Svg src="/icons/clock.svg" className="w-6 h-6" />
                  {radioisotope.halflife}
                </div>
              </div>
              <ButtonEdit path={`/radioisotopes/${radioisotope.id}/edit`} />
            </div>
          </div>
        </>
      )}
    </Page>
  );
};

export default Radioisotope;
