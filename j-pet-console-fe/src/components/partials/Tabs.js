import Svg from "./Svg";

const Tabs = (props) => {
  const { tabs, active, changeContext } = props;
  return (
    <ul className="flex border rounded divide-x">
      {tabs &&
        tabs.map((tab) => (
          <li key={tab.id} className="flex-1">
            <button
              className={`flex justify-center items-center gap-2 w-full h-full p-3 hover:text-sky-600 hover:bg-sky-50 ${
                tab.id === active &&
                "text-sky-600 shadow-[0px_-4px_0px_0px_#0284c7_inset]"
              }`}
              onClick={() => changeContext(tab.id)}
            >
              <Svg src={`/icons/${tab.icon}`} className="w-6 h-6" />
              {tab.name}
            </button>
          </li>
        ))}
    </ul>
  );
};

export default Tabs;
