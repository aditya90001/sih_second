import { useEffect, useState } from 'react';
import { WellMap } from '../components/Map.tsx';
import { ParameterCharts } from '../components/ParameterCharts.tsx';
import type { Alert, Parameter, RiskZone, Well } from '../types/api.ts';

const API = 'http://127.0.0.1:8000/api/v1';

async function getJson<T>(path: string): Promise<T> {
	const response = await fetch(`${API}${path}`);
	if (!response.ok) throw new Error(`${response.status}: ${await response.text()}`);
	return response.json() as Promise<T>;
}

export function Dashboard() {
	const [wells, setWells] = useState<Well[]>([]);
	const [selectedId, setSelectedId] = useState('ACTIVE-001');
	const [nearby, setNearby] = useState<Well[]>([]);
	const [parameters, setParameters] = useState<Parameter[]>([]);
	const [zones, setZones] = useState<RiskZone[]>([]);
	const [alerts, setAlerts] = useState<Alert[]>([]);
	const [error, setError] = useState('');

	const activeWell = wells.find((well) => well.well_id === selectedId) ?? wells[0];

	useEffect(() => {
		getJson<Well[]>('/wells').then(setWells).catch((err: Error) => setError(err.message));
	}, []);

	useEffect(() => {
		if (!activeWell) return;
		Promise.all([
			getJson<Well[]>(`/wells/${activeWell.well_id}/nearby?radius_km=10`),
			getJson<Parameter[]>(`/wells/${activeWell.well_id}/parameters`),
			getJson<RiskZone[]>(`/wells/${activeWell.well_id}/risk-zones?radius_km=10`),
			getJson<Alert[]>(`/alerts?well_id=${activeWell.well_id}`),
		]).then(([nearbyWells, wellParameters, riskZones, wellAlerts]) => {
			setNearby(nearbyWells);
			setParameters(wellParameters);
			setZones(riskZones);
			setAlerts(wellAlerts);
			setError('');
		}).catch((err: Error) => setError(err.message));
	}, [activeWell]);

	return (
		<main className="app-shell">
			<header className="topbar">
				<div><span className="eyebrow">NWIS / DECISION SUPPORT</span><h1>Nearby Wells Intelligence</h1></div>
				<label>ACTIVE WELL<select value={selectedId} onChange={(event) => setSelectedId(event.target.value)}>
					{wells.map((well) => <option key={well.well_id} value={well.well_id}>{well.well_id}</option>)}
				</select></label>
			</header>
			{error && <p className="error">Backend unavailable: {error}</p>}
			{activeWell && <>
				<section className="hero-grid">
					<div className="hero panel"><span className="eyebrow">SYNTHETIC DEMO DATA</span><h2>{activeWell.well_name}</h2><p>{activeWell.field} · {activeWell.operator}</p></div>
					<div className="metric panel"><span>Current depth</span><strong>{activeWell.current_depth.toFixed(0)} m</strong></div>
					<div className="metric panel"><span>Nearby wells</span><strong>{Math.max(0, nearby.length - 1)}</strong></div>
					<div className="metric panel"><span>Risk zones</span><strong>{zones.length}</strong></div>
				</section>
				<section className="content-grid"><div className="panel map-panel"><div className="section-heading"><h2>Nearby well map</h2><span>10 km radius</span></div><WellMap activeWell={activeWell} nearbyWells={nearby} /></div>
					<div className="panel"><div className="section-heading"><h2>Historical risk zones</h2><span>Evidence only</span></div>{zones.length === 0 ? <p className="muted">No repeated historical interval found.</p> : <div className="zone-list">{zones.map((zone) => <div className="zone" key={`${zone.top_depth}-${zone.event_type}`}><strong>{zone.event_type}</strong><span>{zone.top_depth}-{zone.bottom_depth} m · {zone.occurrence_count} events · {zone.well_count} wells</span></div>)}</div>}</div>
				</section>
				<section className="content-grid"><div className="panel"><div className="section-heading"><h2>Active alerts</h2><span>Decision support</span></div>{alerts.length === 0 ? <p className="muted">No active alerts.</p> : alerts.map((alert) => <div className="alert" key={alert.id}><strong>{alert.alert_type} · {alert.severity}</strong><p>{alert.message}</p></div>)}</div><div className="panel"><div className="section-heading"><h2>Well profile</h2></div><p>Total depth <strong>{activeWell.total_depth.toFixed(0)} m</strong></p><p>Events <strong>{activeWell.event_count ?? 0}</strong></p><p>Status <strong>{activeWell.status}</strong></p></div></section>
				<ParameterCharts parameters={parameters} />
			</>}
		</main>
	);
}
