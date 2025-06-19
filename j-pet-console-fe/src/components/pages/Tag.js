import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";

import Tag from "../partials/Tag";
import ButtonBack from "../partials/ButtonBack";
import ButtonEdit from "../partials/ButtonEdit";

import Page from "../partials/Page";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import api from "../../api";

const Experiment = () => {
  const navigate = useNavigate();

  const { tag_id } = useParams();

  const [tag, setTag] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTag = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get(`/tags/${tag_id}`);
      setTag(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate("/");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, [tag_id, navigate]);

  useEffect(() => {
    fetchTag();
  }, [fetchTag, tag_id]);

  return (
    <Page>
      <ButtonBack path="/tags">Back to tags list</ButtonBack>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchTag} />
      ) : (
        <>
          <div className="flex flex-col gap-2">
            <div className="flex justify-between items-center gap-4">
              <h1>{tag.name}</h1>
              <div className="flex gap-4">
                <Tag name={tag.name} color={tag.color} />
              </div>
            </div>
            <div className="grid grid-cols-1 gap-4 pt-2">
              <p className="text-xl">{tag.description}</p>
              <ButtonEdit path={`/tags/${tag.id}/edit`} />
            </div>
          </div>
        </>
      )}
    </Page>
  );
};

export default Experiment;
