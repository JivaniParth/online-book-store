import "./App.css";
import BookStore from "./Components/BookStore";
import { AuthProvider } from "./Components/AuthContext";

export default function App() {
  return (
    <AuthProvider>
      <BookStore />
    </AuthProvider>
  );
}
