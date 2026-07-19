import React, { useState, useEffect, useMemo } from 'react';
import { Search, Building, FolderGit2, CheckCircle, Clock, Database, BarChart3, Settings, Download } from 'lucide-react';
import './index.css';

interface Tender {
  id: number;
  title: string;
  reference_no: string;
  agency: string;
  publishing_date: string;
  status: string;
  awardee?: string;
  award_value?: number;
}

function App() {
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [agencyFilter, setAgencyFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');

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

  const handleScrape = async (monthsBack: number = 0) => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/scrape?agency=eprocure&months_back=${monthsBack}`, {
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

  // Compute filtered data
  const filteredTenders = useMemo(() => {
    return tenders.filter(t => {
      const matchesSearch = t.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                            t.reference_no.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            (t.awardee && t.awardee.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesAgency = agencyFilter === 'All' || t.agency === agencyFilter;
      const matchesStatus = statusFilter === 'All' || t.status === statusFilter;
      
      return matchesSearch && matchesAgency && matchesStatus;
    });
  }, [tenders, searchQuery, agencyFilter, statusFilter]);

  // Compute metrics
  const totalValue = useMemo(() => {
    return tenders.reduce((sum, t) => sum + (t.award_value || 0), 0);
  }, [tenders]);

  const activeCount = useMemo(() => {
    return tenders.filter(t => t.status === 'Active').length;
  }, [tenders]);

  const agencies = ['All', ...Array.from(new Set(tenders.map(t => t.agency)))];
  const statuses = ['All', 'Active', 'Awarded'];

  const formatCurrency = (val?: number) => {
    if (!val) return '-';
    // Format to Indian Rupees roughly, e.g. 1,00,00,000
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);
  };

  return (
    <div className="layout">
      
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand">
          <Database className="brand-icon" size={24} />
          Projects Today
        </div>
        
        <nav className="nav-menu">
          <a href="#" className="nav-item active"><FolderGit2 size={20} /> Project Database</a>
          <a href="#" className="nav-item"><BarChart3 size={20} /> Market Analytics</a>
          <a href="#" className="nav-item"><Building size={20} /> Contractors</a>
          <div style={{flex: 1}}></div>
          <a href="#" className="nav-item"><Settings size={20} /> Settings</a>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        
        <div className="page-header">
          <div className="page-title">
            <h1>Intelligence Dashboard</h1>
            <p>Track live tenders and historical contract awards across India.</p>
          </div>
          <div className="header-actions">
            <button className="btn btn-primary" onClick={() => handleScrape(0)} disabled={loading}>
              <Download size={16} />
              {loading ? 'Syncing...' : 'Sync Live'}
            </button>
            <button className="btn btn-warning" onClick={() => handleScrape(12)} disabled={loading}>
              <Clock size={16} />
              {loading ? 'Extracting...' : 'Deep Archive Sync'}
            </button>
          </div>
        </div>

        {/* Metrics */}
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon blue"><FolderGit2 size={24} /></div>
            <div className="metric-content">
              <h3>Total Projects</h3>
              <div className="value">{tenders.length}</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon green"><CheckCircle size={24} /></div>
            <div className="metric-content">
              <h3>Awarded Value</h3>
              <div className="value" style={{fontSize: '1.4rem'}}>{formatCurrency(totalValue)}</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon orange"><Clock size={24} /></div>
            <div className="metric-content">
              <h3>Active Opportunities</h3>
              <div className="value">{activeCount}</div>
            </div>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="filters-bar">
          <div className="search-input-wrapper">
            <Search size={18} />
            <input 
              type="text" 
              className="search-input" 
              placeholder="Search by title, reference, or contractor..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <select 
            className="filter-select"
            value={agencyFilter}
            onChange={(e) => setAgencyFilter(e.target.value)}
          >
            {agencies.map(a => <option key={a} value={a}>{a === 'All' ? 'All Agencies' : a}</option>)}
          </select>
          
          <select 
            className="filter-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            {statuses.map(s => <option key={s} value={s}>{s === 'All' ? 'All Statuses' : s}</option>)}
          </select>
        </div>

        {/* Data Table */}
        <div className="data-panel">
          <table>
            <thead>
              <tr>
                <th>Project Details</th>
                <th>Agency</th>
                <th>Date</th>
                <th>Value</th>
                <th>Awardee</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredTenders.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                    No projects found matching your criteria. Try syncing data.
                  </td>
                </tr>
              ) : (
                filteredTenders.map((tender) => (
                  <tr key={tender.id}>
                    <td>
                      <div className="project-title" title={tender.title}>{tender.title}</div>
                      <div className="project-ref">{tender.reference_no}</div>
                    </td>
                    <td><span className="agency-badge">{tender.agency}</span></td>
                    <td>{tender.publishing_date}</td>
                    <td style={{fontWeight: 500}}>{formatCurrency(tender.award_value)}</td>
                    <td>
                      {tender.awardee ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <Building size={14} color="var(--text-muted)" />
                          {tender.awardee}
                        </div>
                      ) : (
                        <span style={{ color: 'var(--text-muted)' }}>-</span>
                      )}
                    </td>
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

      </main>
    </div>
  );
}

export default App;
