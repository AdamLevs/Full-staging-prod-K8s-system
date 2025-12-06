import React, { useState, useEffect, useRef } from 'react';
import PreLoader from './PreLoader';
function App() {
  const [services, setServices] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const prevServicesRef = useRef([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const resServices = await fetch('/api/public');
      if (!resServices.ok) throw new Error('Failed to fetch services');
      const newServices = await resServices.json();

      const prevServices = prevServicesRef.current;
      const changed = JSON.stringify(prevServices) !== JSON.stringify(newServices);
      if (changed) {
        setServices(newServices);
        prevServicesRef.current = newServices;

        const resStats = await fetch('/api/services/stats');
        if (resStats.ok) {
          const statsArray = await resStats.json();
          const statsMap = {};
          statsArray.forEach(stat => {
            statsMap[stat.id] = stat;
          });
          setStats(statsMap);
        }
      }
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    if (status === 'UP') return '#10B981';
    if (status === 'DOWN') return '#EF4444';
    return '#FBBF24';
  };

  const getStatusText = (status) => {
    if (status === 'UP') return 'Operational';
    if (status === 'DOWN') return 'Down';
    return 'Unknown';
  };

  if (loading) {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <PreLoader width={80} height={80} />
    </div>
  );
}

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1>Service Status</h1>
        <p>Current operational status of services</p>
      </header>

      {error && (
        <div style={{ backgroundColor: '#FEE2E2', color: '#DC2626', padding: '12px', borderRadius: '8px', marginBottom: '20px' }}>
          Error: {error}
        </div>
      )}

      <div>
        <h2 style={{ marginBottom: '16px' }}>Services</h2>

        {services.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            No services configured yet
          </div>
        ) : (
          <div style={{ border: '1px solid #E5E7EB', borderRadius: '8px' }}>
            {services.map((service, index) => (
              <div
                key={service.id}
                style={{
                  padding: '16px 20px',
                  borderBottom: index < services.length - 1 ? '1px solid #E5E7EB' : 'none'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <h3>{service.name}</h3>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div
                      style={{
                        width: '12px',
                        height: '12px',
                        borderRadius: '50%',
                        backgroundColor: getStatusColor(service.status)
                      }}
                    />
                    <span style={{ color: getStatusColor(service.status) }}>
                      {getStatusText(service.status)}
                    </span>
                  </div>
                </div>

                {/* Extra Monitoring Info */}
                {stats[service.id] && (
                  <div style={{ marginTop: '10px', fontSize: '0.9em', color: '#374151' }}>
                    <p>🧠 CPU Usage: {stats[service.id].cpu_usage ?? 'N/A'}%</p>
                    <p>💾 RAM Usage: {stats[service.id].memory_usage ?? 'N/A'}%</p>
                    <p>🗄️ Disk Usage: {stats[service.id].disk_usage ?? 'N/A'}%</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <footer style={{ textAlign: 'center', marginTop: '40px' }}>
        Last updated: {lastUpdated ? lastUpdated.toLocaleString() : 'N/A'}
      </footer>
    </div>
  );
}

export default App;