import { useState, useEffect } from 'react';
import './index.css';

interface Tender {
  id: number;
  title: string;
  reference_no: string;
  agency: string;
  publishing_date: string;
  status: string;
}

function App() {
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTenders();
  }, []);

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchTenders = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/tenders`);
      if (response.ok) {
        const data = await response.json();
        setTenders(data);
      }
    } catch (error) {
      console.error('Failed to fetch tenders:', error);
    }
  };

  const handleScrape = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/scrape?agency=eprocure`, {
        method: 'POST',
      });
      if (!response.ok) {
          const errorData = await response.json();
          alert(`Scrape failed: ${errorData.detail || 'Unknown error'}`);
      }
      await fetchTenders();
    } catch (error) {
      console.error('Failed to trigger scrape:', error);
      alert(`Scrape failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1>Construction Data Tracker</h1>
        <button className="btn" onClick={handleScrape} disabled={loading}>
          {loading ? 'Scraping...' : 'Scrape eProcure'}
        </button>
      </div>

      <div className="glass-panel">
        <h2>Recent Tenders</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Agency</th>
              <th>Reference No</th>
              <th>Title</th>
              <th>Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {tenders.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                  No tenders found. Click scrape to fetch data.
                </td>
              </tr>
            ) : (
              tenders.map((tender) => (
                <tr key={tender.id}>
                  <td>{tender.id}</td>
                  <td>{tender.agency}</td>
                  <td>{tender.reference_no}</td>
                  <td>{tender.title}</td>
                  <td>{tender.publishing_date}</td>
                  <td>
                    <span className={`status-badge ${tender.status.toLowerCase() === 'active' ? 'status-active' : 'status-closed'}`}>
                      {tender.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
