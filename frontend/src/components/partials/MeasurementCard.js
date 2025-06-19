import Tag from "./Tag";

import Svg from "./Svg";

const MeasurementCard = (props) => {
  const { id, experiment_id, name, description, directory, tags } = props;

  return (
    <a
      href={`/experiments/${experiment_id}/measurements/${id}`}
      className="flex flex-col gap-4 p-4 rounded-lg border border-slate-200 divide-y divide-slate-200 hover:bg-sky-50"
    >
      <div className="grid gap-2">
        <div className="flex justify-between gap-4">
          <h2>{name}</h2>
          <ul className="list-none empty:hidden flex gap-4">
            {tags.map((tag, index) => (
              <li key={index}>
                <Tag {...tag} />
              </li>
            ))}
          </ul>
        </div>
        <div className="flex justify-between gap-4">
          <p>{description}</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 pt-2">
        <div className="flex items-center gap-2 text-sm">
          <Svg src="/icons/command-line.svg" className="w-6 h-6" />
          {directory}
        </div>
      </div>
    </a>
  );
};

export default MeasurementCard;
