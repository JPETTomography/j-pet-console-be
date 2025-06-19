import Svg from "./Svg";

const RadioisotopeCard = (props) => {
  const { id, name, description, activity, halflife } = props;

  return (
    <a
      href={`/radioisotopes/${id}`}
      className="flex flex-col gap-4 p-4 rounded-lg border border-slate-200 divide-y divide-slate-200 hover:bg-sky-50"
    >
      <div className="grid gap-2">
        <div className="flex justify-between gap-4">
          <h2>{name}</h2>
        </div>
        <div className="flex justify-between gap-4">
          <p>{description}</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 pt-2">
        <div className="flex items-center gap-2 text-sm">
          <Svg src="/icons/bolt.svg" className="w-6 h-6" />
          {activity}
        </div>
        <div className="flex items-center gap-2 text-sm">
          <Svg src="/icons/clock.svg" className="w-6 h-6" />
          {halflife}
        </div>
      </div>
    </a>
  );
};

export default RadioisotopeCard;
