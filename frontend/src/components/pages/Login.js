import { CONTACT_MAIL } from "../../const";

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Form from "../partials/Form";
import InputPassword from "../partials/Input/InputPassword";
import InputText from "../partials/Input/InputText";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const validateForm = () => {
    if (!email || !password) {
      setError("Email and password are required");
      return false;
    }
    setError("");
    return true;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!validateForm()) return;
    setLoading(true);

    const formDetails = new URLSearchParams();
    formDetails.append("username", email);
    formDetails.append("password", password);

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_SOURCE}/token`,
        {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: formDetails,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.detail || "Authentication failed!");
      } else {
        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));
        setLoading(false);
        navigate("/experiments");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <div className="flex-1 flex justify-center items-center p-4">
        <section className="grid gap-16 w-full max-w-lg">
          <img
            src="/images/logos/logo-full-v.svg"
            alt="J-PET logotype"
            className="w-20"
          />

          <h1 className="text-center">Login</h1>
          <Form onSubmit={handleSubmit}>
            <InputText name="email" setValue={setEmail} required />

            <div className="grid gap-2">
              <InputPassword setPassword={setPassword} />

              <a
                href={`mailto:${CONTACT_MAIL}`}
                className="max-w-max ml-auto text-xs text-slate-700 hover:text-slate-900 hover:underline focus:outline-offset-4"
              >
                Forgot password
              </a>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary !max-w-none"
            >
              {loading ? "Logging in..." : "Login"}
            </button>
            {error && <p className="text-rose-700">{error}</p>}
          </Form>
          <p className="text-center">
            You don't have an account yet?
            <br />
            Please contact with our{" "}
            <a
              href={`mailto:${CONTACT_MAIL}`}
              className="link-primary !inline-flex"
            >
              administration
            </a>
            .
          </p>
        </section>
      </div>
      <div
        style={{
          backgroundImage: `url(${
            process.env.PUBLIC_URL + "/images/login-bg.png"
          })`,
        }}
        className="hidden lg:block overflow-hidden bg-cover bg-top bg-no-repeat"
      ></div>
    </div>
  );
};

export default Login;
