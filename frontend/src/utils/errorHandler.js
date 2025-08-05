import { getCurrentUser } from "./permissions";

export const handleApiError = (error, navigate, setError) => {
  if (error.response?.status === 401) {
    const token = localStorage.getItem("token");
    const user = getCurrentUser();
    
    if (!token || !user) {
      navigate("/");
    } else {
      setError("You don't have permission to access this resource.");
    }
  } else if (error.response?.status === 403) {
    setError("You don't have permission to access this resource.");
  } else {
    setError(error.message || "An error occurred");
  }
};

export default handleApiError;
