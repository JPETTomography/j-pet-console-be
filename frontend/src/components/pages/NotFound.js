import Page from "../partials/Page";

const NotFound = () => {
  return (
    <Page>
      <div className="flex-1 flex flex-col justify-center items-center gap-6 font-medium">
        <img src="/images/404.png" alt="404 error graphics" className="w-72" />
        <h1>Page Not Found</h1>
        <div>
          <p>Unfortunately, the page you're looking for could not be found.</p>
          <p>Please check if the URL is correct or return to the homepage.</p>
        </div>
        <a href="/" className="text-sky-700 hover:text-sky-900 hover:underline">
          Back to main page
        </a>
      </div>
    </Page>
  );
};

export default NotFound;
