import Header from "./Header";

const Page = (props) => {
  const { children } = props;
  const currentUser = JSON.parse(localStorage.getItem("user"));


  return (
    <>
      <Header currentUser={currentUser} />
      <main className="flex-1 flex flex-col gap-8 w-full max-w-screen-2xl p-6 mx-auto">
        {children}
      </main>
    </>
  );
};

export default Page;
