import { Navigate } from "react-router-dom";
import { canAccessRoute } from "../../utils/permissions";

const ProtectedRoute = ({ children, route }) => {
  const hasAccess = canAccessRoute(route);
  
  if (!hasAccess) {
    return <Navigate to="/experiments" replace />;
  }
  
  return children;
};

export default ProtectedRoute;
