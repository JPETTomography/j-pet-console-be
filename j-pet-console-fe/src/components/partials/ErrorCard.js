import Svg from "../partials/Svg";

const ErrorCard = (props) => {
  const { children } = props;

  return (
    <div className="flex gap-4 w-full max-w-4xl p-4 rounded-xl bg-rose-50 border border-rose-700 text-rose-700">
      <Svg src="/icons/exclamation-circle.svg" className="w-6 h-6" />
      {children}
    </div>
  );
};

export default ErrorCard;
