import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";

import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import TagForm from "../partials/TagForm";

import api from "../../api";

const TagEdit = () => {
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
  }, [fetchTag]);

  return (
    <Page>
      <ButtonBack path={`/tags/${tag.id}`}>Back to the tag</ButtonBack>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchTag} />
      ) : (
        <>
          <h1>Edit tag - {tag.name}</h1>
          <TagForm tag={tag} />
        </>
      )}
    </Page>
  );
};

export default TagEdit;
