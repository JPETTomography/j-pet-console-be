import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";

import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import UserForm from "../partials/UserForm";

import api from "../../api";

const UserEdit = () => {
  const navigate = useNavigate();
  const { user_id } = useParams();

  const [user, setUser] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchUser = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/users/${user_id}`);
      setUser(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate("/");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, [user_id, navigate]);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  return (
    <Page>
      <ButtonBack path={`/users/${user.id}`}>Back to the user</ButtonBack>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchUser} />
      ) : (
        <>
          <h1>Edit user - {user.name}</h1>
          <UserForm user={user} />
        </>
      )}
    </Page>
  );
};

export default UserEdit;