import asyncio
import json
import random
import websockets

async def simulate_drilling_stream(uri: str, well_id: str):
    async with websockets.connect(uri) as websocket:
        print(f"Connected to eRTMAC WebSocket for well: {well_id}")
        depth = 2760.0
        
        while depth <= 3000.0:
            depth += random.uniform(0.5, 1.5)
            # Simulate parameter drift approaching risk formation
            is_risk_zone = 2800.0 <= depth <= 3000.0
            
            payload = {
                "well_id": well_id,
                "timestamp": depth,
                "depth": round(depth, 2),
                "rop": round(random.uniform(5.0, 15.0) if not is_risk_zone else random.uniform(1.0, 4.0), 2),
                "wob": round(random.uniform(8.0, 14.0), 2),
                "rpm": round(random.uniform(100.0, 140.0), 2),
                "torque": round(random.uniform(12.0, 18.0) if not is_risk_zone else random.uniform(25.0, 38.0), 2),
                "mud_weight": round(1.15, 2),
                "ecd": round(1.22 if not is_risk_zone else 1.10, 2),
                "flow_rate": round(random.uniform(1100, 1250), 1)
            }

            await websocket.send(json.dumps(payload))
            print(f"Sent stream telemetry at Depth: {depth:.2f} m")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(simulate_drilling_stream("ws://localhost:8000/api/v1/ws/drilling/ACTIVE-001", "ACTIVE-001"))