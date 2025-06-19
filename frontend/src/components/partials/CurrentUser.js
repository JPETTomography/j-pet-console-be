import { useNavigate } from "react-router-dom";

import Svg from "./Svg";

const CurrentUser = (props) => {
  const { currentUser } = props;
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <button
      type="button"
      onClick={handleLogout}
      className="flex items-center gap-2 outline-offset-4"
    >
      <div className="flex flex-col items-end">
        <span className="font-semibold">{currentUser?.name}</span>
        <span className="text-sm text-slate-600">{currentUser?.email}</span>
      </div>
      <Svg src="/icons/chevron-down.svg" className="w-6 h-6 text-slate-400" />
    </button>
  );
};

export default CurrentUser;
