import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { Parameter } from '../types/api';

export function ParameterCharts({ parameters }: { parameters: Parameter[] }) {
	return (
		<div className="chart-grid">
			{(['rop', 'torque', 'wob', 'rpm', 'mud_weight', 'standpipe_pressure'] as const).map((key) => (
				<section className="panel chart-panel" key={key}>
					  <h3>{key.replace(/_/g, ' ').toUpperCase()}</h3>
					<ResponsiveContainer width="100%" height={180}>
						<LineChart data={parameters}>
							<XAxis dataKey="depth" tick={{ fill: '#64748b', fontSize: 10 }} />
							<YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
							<Tooltip />
							<Line type="monotone" dataKey={key} stroke="#168aad" dot={false} strokeWidth={2} />
						</LineChart>
					</ResponsiveContainer>
				</section>
			))}
		</div>
	);
}
