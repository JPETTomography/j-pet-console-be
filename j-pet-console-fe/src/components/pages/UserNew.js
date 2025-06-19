import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";

import UserForm from "../partials/UserForm";

const UserNew = () => {
  return (
    <Page>
      <ButtonBack path="/users">Back to users list</ButtonBack>
      <h1>New user</h1>
      <UserForm />
    </Page>
  );
};

export default UserNew;
