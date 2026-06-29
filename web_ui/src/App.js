import React, { useState } from "react";
import "./App.css";

function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
  };

  const handleSearch = async (term = searchTerm) => {
    if (!term.trim()) return;

    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:5000/search?q=${term}`);
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error("Search failed:", err);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">

        <h1 className="title">UCI ICS Search Engine</h1>

        <div className="search-wrapper">
          <input
            type="text"
            value={searchTerm}
            onChange={handleChange}
            className="search-input"
            placeholder="Search documents..."
          />

          <button className="search-btn" onClick={() => handleSearch()}>
            Search
          </button>
        </div>

        {/* Results Section */}
        <div className="results-container">
          {loading && <p>Searching...</p>}

          {!loading && results.length > 0 && (
            <ul className="results-list">
              {results.map((item, i) => (
                <li key={i} className="result-card">
                  <a href={item.url} target="_blank" rel="noreferrer" className="result-link">
                    {item.url}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;