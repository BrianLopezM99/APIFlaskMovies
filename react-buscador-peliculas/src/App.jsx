import "./App.css";
import { useMovies } from "./hooks/useMovies";
import { Movies } from "./components/movies";
import { useSearch } from "./hooks/useSearch";
import { useState } from "react";

function App() {

  const [sort, setSort] = useState(false)

  const { search, setSearch, error } = useSearch();
  const { mappedMovies, loading, getMovies } = useMovies({ search, sort });

  const handleSubmit = (e) => {
    e.preventDefault();
    getMovies();
  };

  const handleSort = () => {
    setSort(!sort)
  }

  const handleChange = (e) => {
    setSearch(e.target.value);
  };

  return (
    <div className="page">
      <header className="header-page">
        <h1>Buscador de peliculas 🔍</h1>
        <form className="form" onSubmit={handleSubmit}>
          <input
            value={search}
            onChange={handleChange}
            name="query"
            placeholder="Avengers, Star Wars, Super Mario..."
            type="text"
          />
          <input type="checkbox" onChange={handleSort} checked={sort} />
          <button type="submit">Buscar</button>
        </form>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </header>

      <main>
        {loading ? <p>Cargando...</p> : <Movies movies={mappedMovies} />}
      </main>
    </div>
  );
}

export default App;
