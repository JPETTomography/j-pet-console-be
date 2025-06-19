import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import TagCard from "../partials/TagCard";
import Page from "../partials/Page";
import PaginatedItems from "../partials/PaginatedItems";
import ButtonNew from "../partials/ButtonNew";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import api from "../../api";

const TagsList = () => {
  const navigate = useNavigate();

  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTags = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get("/tags");
      setTags(response.data);
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
    fetchTags();
  }, [fetchTags]);

  return (
    <Page>
      <h1>Tags List</h1>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchTags} />
      ) : (
        <PaginatedItems
          items={tags}
          ItemComponent={TagCard}
          newButton={<ButtonNew path="/tags/new">Add new tag</ButtonNew>}
        />
      )}
    </Page>
  );
};

export default TagsList;
