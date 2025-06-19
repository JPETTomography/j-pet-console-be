import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import UserCard from "../partials/UserCard";
import ButtonNew from "../partials/ButtonNew";

import Page from "../partials/Page";
import PaginatedItems from "../partials/PaginatedItems";

import FetchLoading from "../partials/FetchLoading";
import FetchError from "../partials/FetchError";
import api from "../../api";

const UsersList = () => {
  const navigate = useNavigate();

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get("/users");
      setUsers(response.data);
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
    fetchUsers();
  }, [fetchUsers]);

  return (
    <Page>
      <h1>Users List</h1>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchUsers} />
      ) : (
        <PaginatedItems
          items={users}
          ItemComponent={UserCard}
          newButton={<ButtonNew path="/users/new">Add new user</ButtonNew>}
        />
      )}
    </Page>
  );
};

export default UsersList;
