"""
AUTOMA Processing Engine - Metrics Engine.

Registers, aggregates, and reports processing and rendering benchmarks.
Maintains in-memory node-level metrics and queries history table for system averages.
"""

import logging
from typing import Any, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History

logger = logging.getLogger("automa.processing.engine.metrics")


class MetricsEngine:
    """Computes averages and rates for rendering benchmark dashboards."""

    _instance: Any = None

    def __new__(cls, *args, **kwargs) -> "MetricsEngine":
        if not cls._instance:
            cls._instance = super(MetricsEngine, cls).__new__(cls, *args, **kwargs)
            cls._instance._node_accumulators = {
                "import": [], "crop": [], "resize": [], "scale": [], "zoom": [],
                "rotate": [], "mirror": [], "brightness": [], "contrast": [], "saturation": [],
                "sharpness": [], "noisereduction": [], "framerate": [], "bitrate": [], "codec": [],
                "audiovolume": [], "audiofadein": [], "audiofadeout": [], "metadatacleaner": [], "export": []
            }
        return cls._instance

    def __init__(self) -> None:
        pass

    def record_node_time(self, node_type: str, elapsed_seconds: float) -> None:
        """Record the execution duration of a specific pipeline node type in memory."""
        node_key = node_type.lower()
        if node_key in self._node_accumulators:
            self._node_accumulators[node_key].append(elapsed_seconds)
            # Cap array size to last 100 entries for rolling average
            if len(self._node_accumulators[node_key]) > 100:
                self._node_accumulators[node_key].pop(0)

    def get_average_node_times(self) -> Dict[str, float]:
        """Compute the average duration for each node type based on recorded times."""
        averages = {}
        for node, times in self._node_accumulators.items():
            if times:
                averages[node] = round(sum(times) / len(times), 2)
            else:
                averages[node] = 0.0
        return averages

    async def get_project_benchmarks(self, session: AsyncSession, project_id: str) -> Dict[str, Any]:
        """
        Query database history logs to generate full performance metrics.
        Returns:
            Dict containing avg render time, speed, success rate, and resource averages.
        """
        stmt = (
            select(
                func.count(History.id).label("total"),
                func.avg(History.execution_time).label("avg_time"),
                func.avg(History.speed).label("avg_speed"),
                func.avg(History.cpu_usage).label("avg_cpu"),
                func.avg(History.ram_usage).label("avg_ram"),
                func.avg(History.gpu_usage).label("avg_gpu"),
                func.sum(select(func.count(History.id)).where(History.status == "completed").scalar_subquery()).label("success"),
                func.sum(select(func.count(History.id)).where(History.status == "failed").scalar_subquery()).label("failed")
            )
            .where(History.project_id == project_id)
        )
        
        result = await session.execute(stmt)
        row = result.first()
        
        if not row or not row.total:
            return {
                "total_jobs": 0,
                "avg_render_time": 0.0,
                "avg_speed": 0.0,
                "success_rate": 0.0,
                "error_rate": 0.0,
                "avg_cpu_usage": 0.0,
                "avg_ram_usage": 0.0,
                "avg_gpu_usage": 0.0,
                "node_averages": self.get_average_node_times()
            }

        total = row.total
        # Handle SQLite sum returning None
        completed = row.success if row.success is not None else 0
        failed = row.failed if row.failed is not None else 0
        
        success_rate = (completed / total) * 100.0 if total > 0 else 0.0
        error_rate = (failed / total) * 100.0 if total > 0 else 0.0

        return {
            "total_jobs": total,
            "avg_render_time": round(float(row.avg_time or 0.0), 2),
            "avg_speed": round(float(row.avg_speed or 0.0), 1),
            "success_rate": round(success_rate, 1),
            "error_rate": round(error_rate, 1),
            "avg_cpu_usage": round(float(row.avg_cpu or 0.0), 1),
            "avg_ram_usage": round(float(row.avg_ram or 0.0), 1),
            "avg_gpu_usage": round(float(row.avg_gpu or 0.0), 1),
            "node_averages": self.get_average_node_times()
        }


# Global singleton instance
metrics_engine = MetricsEngine()
