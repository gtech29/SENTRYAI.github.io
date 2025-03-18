import React, { useState, useEffect } from 'react';
import { Navbar, Nav, Container, Table, Button, Spinner, Alert } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import logo from './logo.jpg';

interface Log {
  id: number;
  timestamp: string;
  source_ip: string;
  event_type: string;
  anomaly_score: number;
}

function App() {
  const [logs, setLogs] = useState<Log[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [criticalAlerts, setCriticalAlerts] = useState<Log[]>([]);

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchLogs = () => {
    setLoading(true);
    fetch('http://localhost:5000/logs')
      .then(response => response.json())
      .then(data => {
        setLogs(data);
        setCriticalAlerts(data.filter((log: Log) => log.anomaly_score > 0.7));
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching logs:', error);
        setLoading(false);
      });
  };

  const generateNewData = () => {
    fetch('http://localhost:5000/generate-data', { method: 'POST' })
      .then(response => response.json())
      .then(() => fetchLogs())
      .catch(error => console.error('Error generating data:', error));
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar Navigation */}
      <Navbar bg="light" expand="lg" className="flex-column" style={{ width: '250px', height: '100vh' }}>
        <Navbar.Brand href="#" className="mb-4 d-flex justify-content-center">
          <img src={logo} alt="Logo" className="center" style={{ width: '80%', height: 'auto' }} />
        </Navbar.Brand>
        <Nav className="flex-column">
          <Nav.Link href="#dashboard">Dashboard</Nav.Link>
          <Nav.Link href="#more-information">More Information</Nav.Link>
          <Nav.Link href="#contact-me">Contact Me</Nav.Link>
        </Nav>
      </Navbar>

      {/* Main Dashboard Content */}
      <div style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>
        <Container>
          <h1 className="text-center">IDS Dashboard</h1>
          <Button variant="primary" onClick={generateNewData} className="mb-3 w-100">
        Generate New Data
          </Button>
          {loading && <Spinner animation="border" variant="primary" className="mb-3 d-block mx-auto" />}
          {criticalAlerts.length > 0 && (
        <Alert variant="danger" className="mb-3">
          <h4 className="text-center">Critical Anomalies Detected ({criticalAlerts.length})</h4>
          <ul>
            {criticalAlerts.map(alert => (
          <li key={alert.id}>
            {alert.timestamp} - {alert.source_ip} - Score: {alert.anomaly_score.toFixed(2)}
          </li>
            ))}
          </ul>
        </Alert>
          )}
          <Table striped bordered hover responsive>
        <thead>
          <tr>
            <th>ID</th>
            <th>Timestamp</th>
            <th>Source IP</th>
            <th>Event Type</th>
            <th>Anomaly Score</th>
          </tr>
        </thead>
        <tbody>
          {logs.map(log => (
            <tr
          key={log.id}
          style={{
            backgroundColor: log.anomaly_score > 0.5 ? '#ffcccc' : 'transparent',
            fontWeight: log.anomaly_score > 0.5 ? 'bold' : 'normal',
          }}
            >
          <td>{log.id}</td>
          <td>{log.timestamp}</td>
          <td>{log.source_ip}</td>
          <td>{log.event_type}</td>
          <td>{log.anomaly_score.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
          </Table>
          {logs.length > 0 && (
        <p className="mt-3 text-center">
          Total Logs: {logs.length} | Anomalies Detected: {logs.filter(log => log.anomaly_score > 0.5).length}
        </p>
          )}
        </Container>
      </div>
    </div>
  );
}

export default App;
