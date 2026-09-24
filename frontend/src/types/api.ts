export type Well = {
	id: number;
	well_id: string;
	well_name: string;
	latitude: number;
	longitude: number;
	total_depth: number;
	current_depth: number;
	field: string;
	operator: string;
	well_type: string;
	status: string;
	data_source_type: string;
	distance_km?: number;
	event_count?: number;
	risk_summary?: Record<string, number>;
};

export type Parameter = {
	depth: number;
	rop: number;
	wob: number;
	rpm: number;
	torque: number;
	mud_weight: number;
	standpipe_pressure: number;
};

export type RiskZone = {
	top_depth: number;
	bottom_depth: number;
	formation: string;
	event_type: string;
	occurrence_count: number;
	well_count: number;
};

export type Alert = {
	id: number;
	depth: number;
	alert_type: string;
	severity: string;
	message: string;
	status: string;
};
