import Badge from "./Badge";

import Svg from "./Svg";

const DetectorCard = (props) => {
  const { id, name, description, status, agent_code } = props;

  return (
    <a
      href={`/detectors/${id}`}
      className="flex flex-col gap-4 p-4 rounded-lg border border-slate-200 divide-y divide-slate-200 hover:bg-sky-50"
    >
      <div className="grid gap-2">
        <div className="flex justify-between gap-4">
          <h2>{name}</h2>
          <div className="flex gap-4">
            <Badge status={status} />
          </div>
        </div>
        <div className="flex justify-between gap-4">
          <p>{description}</p>
        </div>
      </div>
      <div className="grid grid-cols-1 gap-4 pt-2">
        <div className="flex items-center gap-2 text-sm">
          <Svg src="/icons/globe-europe-africa.svg" className="w-6 h-6" />
          {agent_code}
        </div>
      </div>
    </a>
  );
};

export default DetectorCard;
