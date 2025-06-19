import Badge from "./Badge";

import Svg from "./Svg";

const UserCard = (props) => {
  const { id, name, email, role } = props;

  return (
    <a
      href={`/users/${id}`}
      className="flex flex-col gap-4 p-4 rounded-lg border border-slate-200 divide-y divide-slate-200 hover:bg-sky-50"
    >
      <div className="grid gap-2">
        <div className="flex justify-between gap-4">
          <h2>{name}</h2>
          {role && (
            <div className="flex gap-4">
              <Badge status={role} />
            </div>
          )}
        </div>
        <div className="grid grid-cols-1 gap-4 pt-2">
          <div className="flex items-center gap-2 text-sm">
            <Svg src="/icons/at-symbol.svg" className="w-6 h-6" />
            {email}
          </div>
        </div>
      </div>
    </a>
  );
};

export default UserCard;
