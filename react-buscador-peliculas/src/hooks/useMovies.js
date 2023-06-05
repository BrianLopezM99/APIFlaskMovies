import { useState, useRef } from "react";
import { searchMovies } from "../services/movies.js";

export function useMovies({ search, sort }) {
  const [mappedMovies, setMappedMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const previousSearch = useRef(search);

  const getMovies = async () => {
    if (search === previousSearch.current) return;

    try {
      setLoading(true);
      setError(null);
      previousSearch.current = search;
      const newMovies = await searchMovies({ search });
      setMappedMovies(newMovies);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const sortedMovies = sort
    ? [...mappedMovies].sort((a, b) => a.title.localeCompare(b.title))
    : mappedMovies;

  return { mappedMovies: sortedMovies, getMovies, loading, error };
}
