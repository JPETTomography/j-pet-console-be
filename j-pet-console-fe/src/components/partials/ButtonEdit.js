import Svg from "../partials/Svg";

const ButtonEdit = (props) => {
  const { path, children } = props;

  return (
    <a href={path} className="btn-primary-outline">
      <Svg src="/icons/pencil.svg" className="w-5 h-5" />
      {children || "Edit"}
    </a>
  );
};

export default ButtonEdit;
