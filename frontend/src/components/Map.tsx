import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet';
import type { Well } from '../types/api';
import 'leaflet/dist/leaflet.css';

type Props = { activeWell: Well; nearbyWells: Well[] };

export function WellMap({ activeWell, nearbyWells }: Props) {
	return (
		<MapContainer center={[activeWell.latitude, activeWell.longitude]} zoom={11} className="map">
			<TileLayer
				attribution='&copy; OpenStreetMap contributors'
				url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
			/>
			<CircleMarker center={[activeWell.latitude, activeWell.longitude]} pathOptions={{ color: '#168aad' }} radius={9}>
				<Popup>{activeWell.well_name} (active well)</Popup>
			</CircleMarker>
			{nearbyWells.filter((well) => well.well_id !== activeWell.well_id).map((well) => (
				<CircleMarker
					key={well.well_id}
					center={[well.latitude, well.longitude]}
					pathOptions={{ color: (well.event_count ?? 0) >= 5 ? '#c2410c' : '#2f855a' }}
					radius={7}
				>
					<Popup>
						<strong>{well.well_name}</strong><br />
						{well.distance_km?.toFixed(2)} km | {well.event_count ?? 0} events
					</Popup>
				</CircleMarker>
			))}
		</MapContainer>
	);
}
