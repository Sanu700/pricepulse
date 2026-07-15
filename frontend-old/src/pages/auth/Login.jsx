import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login as loginService } from "../../services/authService";
import { useAuth } from "../../hooks/useAuth";

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    try {
      const data = await loginService({
        username,
        password,
      });

      login(data);

      navigate("/");
    } catch (error) {
      alert("Invalid username or password");
      console.error(error);
    }
  }

  return (
    <div className="mx-auto mt-24 max-w-md rounded-xl border border-gray-200 bg-white p-8 shadow-lg">
      <h1 className="mb-6 text-center text-3xl font-bold text-purple-600">
        Login
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Username"
          className="w-full rounded-lg border p-3 outline-none focus:border-purple-500"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full rounded-lg border p-3 outline-none focus:border-purple-500"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          type="submit"
          className="w-full rounded-lg bg-purple-600 py-3 font-semibold text-white transition hover:bg-purple-700"
        >
          Login
        </button>
      </form>
    </div>
  );
}

export default Login;