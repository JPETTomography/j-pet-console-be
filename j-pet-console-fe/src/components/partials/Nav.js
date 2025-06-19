import { NavLink } from "react-router-dom";

function navForRole(role) {
  switch (role) {
    case "shifter":
      return ["experiments", "tags", "radioisotopes"];
    case "coordinator":
      return ["experiments", "detectors", "tags", "radioisotopes"];
    case "admin":
      return ["users", "experiments", "detectors", "tags", "radioisotopes"];
    default:
      return ["experiments"];
  }
}

const Nav = (props) => {
  const { currentUserRole } = props;

  return (
    <nav>
      <ul className="list-none flex items-center gap-16">
        {navForRole(currentUserRole).map((navlink, index) => {
          return (
            <li key={index}>
              <NavLink
                to={`/${navlink}`}
                className={({ isActive }) => {
                  return `capitalize font-medium outline-offset-4 ${
                    isActive
                      ? "font-bold text-sky-700 hover:text-sky-900 underline"
                      : "hover:text-sky-700 hover:underline"
                  }`;
                }}
              >
                {navlink}
              </NavLink>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

export default Nav;
