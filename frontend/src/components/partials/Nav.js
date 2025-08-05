import { NavLink } from "react-router-dom";

function navForRole(role) {
  const baseNav = ["experiments", "detectors", "tags", "radioisotopes"];
  
  switch (role) {
    case "admin":
      return ["users", ...baseNav];
    case "coordinator":
    case "shifter":
    default:
      return baseNav;
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
