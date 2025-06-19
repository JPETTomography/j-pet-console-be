import { useState } from "react";

import Svg from "../components/partials/Svg";

const usePasswordToggle = () => {
  const [visible, setVisibility] = useState(false);

  const InputType = visible ? "text" : "password";

  const Icon = (
    <button
      type="button"
      onClick={() => setVisibility((visible) => !visible)}
      className="absolute top-2.5 right-2 text-slate-400 outline-offset-2 hover:text-slate-600 focus:text-slate-600"
    >
      <Svg
        src={visible ? "/icons/eye-slash.svg" : "/icons/eye.svg"}
        className="w-8 h-8"
      />
    </button>
  );

  return [InputType, Icon];
};

export default usePasswordToggle;
