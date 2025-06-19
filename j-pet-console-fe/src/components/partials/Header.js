import HomepageButton from "./HomepageButton";
import Nav from "./Nav";
import CurrentUser from "./CurrentUser";

const Header = (props) => {
  const { currentUser } = props;

  return (
    <header className="flex justify-between items-center gap-4 h-14 px-6 py-2 border-b">
      <HomepageButton />
      <Nav currentUserRole={currentUser?.role} />
      <CurrentUser currentUser={currentUser} />
    </header>
  );
};

export default Header;
