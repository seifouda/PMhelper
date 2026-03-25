"""
Analysis Service

Service layer that wraps existing PMHelper analysis engines (CPM, PERT, RCPS)
to provide async analysis capabilities for the FastAPI server.
"""

import asyncio
import traceback
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import uuid
import logging
import pandas as pd
import json

# Import existing analysis engines
from ...core.cpm_analyzer import CPMAnalyzer
from ...core.pert_analyzer import PERTAnalyzer
from ...core.rcps_analyzer import RCPSAnalyzer
from ..api.models.schemas import AnalysisType, CPMActivity, PERTActivity, RCPSActivity
from ..database.models import AnalysisJob
from ..config import config

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for running PMHelper analysis engines asynchronously."""
    
    def __init__(self):
        self._running_jobs = {}
        self._job_queue = asyncio.Queue()
        self._worker_task = None
        
    async def start_worker(self):
        """Start the analysis worker task."""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._analysis_worker())
    
    async def stop_worker(self):
        """Stop the analysis worker task."""
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
    
    async def _analysis_worker(self):
        """Background worker that processes analysis jobs."""
        logger.info("Analysis worker started")
        
        while True:
            try:
                job_data = await self._job_queue.get()
                job_id = job_data["job_id"]
                
                # Track running job
                self._running_jobs[job_id] = job_data
                
                # Process the analysis
                await self._process_analysis_job(job_data)
                
                # Remove from running jobs
                self._running_jobs.pop(job_id, None)
                
            except asyncio.CancelledError:
                logger.info("Analysis worker cancelled")
                break
            except Exception as e:
                logger.error(f"Error in analysis worker: {e}")
                logger.error(traceback.format_exc())
    
    async def submit_cpm_analysis(self, 
                                activities: List[CPMActivity], 
                                project_id: Optional[str] = None,
                                options: Optional[Dict[str, Any]] = None) -> str:
        """Submit a CPM analysis job."""
        job_id = str(uuid.uuid4())
        
        job_data = {
            "job_id": job_id,
            "analysis_type": AnalysisType.CPM,
            "project_id": project_id,
            "activities": [activity.dict() for activity in activities],
            "options": options or {},
            "created_at": datetime.now(timezone.utc)
        }
        
        await self._job_queue.put(job_data)
        logger.info(f"Submitted CPM analysis job: {job_id}")
        
        return job_id
    
    async def submit_pert_analysis(self, 
                                 activities: List[PERTActivity], 
                                 project_id: Optional[str] = None,
                                 target_duration: Optional[float] = None,
                                 confidence_level: float = 0.95,
                                 options: Optional[Dict[str, Any]] = None) -> str:
        """Submit a PERT analysis job."""
        job_id = str(uuid.uuid4())
        
        job_data = {
            "job_id": job_id,
            "analysis_type": AnalysisType.PERT,
            "project_id": project_id,
            "activities": [activity.dict() for activity in activities],
            "target_duration": target_duration,
            "confidence_level": confidence_level,
            "options": options or {},
            "created_at": datetime.now(timezone.utc)
        }
        
        await self._job_queue.put(job_data)
        logger.info(f"Submitted PERT analysis job: {job_id}")
        
        return job_id
    
    async def submit_rcps_analysis(self, 
                                 activities: List[RCPSActivity], 
                                 resource_limits: Dict[str, float],
                                 project_id: Optional[str] = None,
                                 options: Optional[Dict[str, Any]] = None) -> str:
        """Submit an RCPS analysis job."""
        job_id = str(uuid.uuid4())
        
        job_data = {
            "job_id": job_id,
            "analysis_type": AnalysisType.RCPS,
            "project_id": project_id,
            "activities": [activity.dict() for activity in activities],
            "resource_limits": resource_limits,
            "options": options or {},
            "created_at": datetime.now(timezone.utc)
        }
        
        await self._job_queue.put(job_data)
        logger.info(f"Submitted RCPS analysis job: {job_id}")
        
        return job_id
    
    async def _process_analysis_job(self, job_data: Dict[str, Any]):
        """Process an individual analysis job."""
        job_id = job_data["job_id"]
        analysis_type = job_data["analysis_type"]
        
        try:
            logger.info(f"Starting analysis job {job_id} (type: {analysis_type})")
            
            # Call the appropriate analysis method
            if analysis_type == AnalysisType.CPM:
                results = await self._run_cpm_analysis(job_data)
            elif analysis_type == AnalysisType.PERT:
                results = await self._run_pert_analysis(job_data)
            elif analysis_type == AnalysisType.RCPS:
                results = await self._run_rcps_analysis(job_data)
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
            
            logger.info(f"Completed analysis job {job_id}")
            # Store results (this would be handled by the route that calls this service)
            
        except Exception as e:
            logger.error(f"Failed analysis job {job_id}: {e}")
            logger.error(traceback.format_exc())
            raise
    
    async def _run_cpm_analysis(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run CPM analysis using existing CPMAnalyzer."""
        activities_data = job_data["activities"]
        
        def _cmp_analysis():
            """Synchronous CPM analysis in thread."""
            analyzer = CPMAnalyzer()
            
            # Convert activities to the format expected by the existing analyzer
            formatted_activities = []
            for activity in activities_data:
                formatted_activity = {
                    'id': activity['id'],
                    'name': activity['name'],
                    'duration': activity['duration'],
                    'predecessors': activity['predecessors'],
                    'resource': activity.get('resource', 'Default'),
                    'cost': activity.get('cost', 0),
                    'min_duration': activity.get('crash_duration', activity['duration']),
                    'crash_cost': activity.get('crash_cost', 0)
                }
                formatted_activities.append(formatted_activity)
            
            # Run the analysis
            graph, critical_paths, critical_activities = analyzer.analyze(formatted_activities)
            
            # Convert results to JSON-serializable format
            results = {
                'analysis_type': 'cpm',
                'project_duration': max([graph.nodes[node].get('latest_finish', 0) 
                                       for node in graph.nodes() if 'latest_finish' in graph.nodes[node]]),
                'critical_path': critical_paths[0] if critical_paths else [],
                'critical_activities': critical_activities,
                'activities': []
            }
            
            # Extract activity results
            for node in graph.nodes():
                node_data = graph.nodes[node]
                if 'activity_id' in node_data:
                    activity_result = {
                        'id': node_data.get('activity_id'),
                        'name': node_data.get('name', ''),
                        'duration': node_data.get('duration', 0),
                        'earliest_start': node_data.get('earliest_start', 0),
                        'earliest_finish': node_data.get('earliest_finish', 0),
                        'latest_start': node_data.get('latest_start', 0),
                        'latest_finish': node_data.get('latest_finish', 0),
                        'total_float': node_data.get('total_float', 0),
                        'free_float': node_data.get('free_float', 0),
                        'is_critical': node_data.get('activity_id') in critical_activities,
                        'resource': node_data.get('resource', ''),
                        'cost': node_data.get('cost', 0)
                    }
                    results['activities'].append(activity_result)
            
            return results
        
        # Run in thread to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _cmp_analysis)
    
    async def _run_pert_analysis(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run PERT analysis using existing PERTAnalyzer."""
        activities_data = job_data["activities"]
        target_duration = job_data.get("target_duration")
        confidence_level = job_data.get("confidence_level", 0.95)
        
        def _pert_analysis():
            """Synchronous PERT analysis in thread."""
            analyzer = PERTAnalyzer()
            
            # Convert activities to the format expected by the existing analyzer
            formatted_activities = []
            for activity in activities_data:
                # Calculate expected time and variance
                optimistic = activity.get('optimistic_duration', activity['duration'] * 0.8)
                most_likely = activity.get('most_likely_duration', activity['duration'])
                pessimistic = activity.get('pessimistic_duration', activity['duration'] * 1.2)
                
                expected_time = (optimistic + 4 * most_likely + pessimistic) / 6
                variance = ((pessimistic - optimistic) / 6) ** 2
                
                formatted_activity = {
                    'id': activity['id'],
                    'name': activity['name'],
                    'duration': expected_time,  # Use expected time as duration
                    'optimistic_time': optimistic,
                    'most_likely_time': most_likely,
                    'pessimistic_time': pessimistic,
                    'expected_time': expected_time,
                    'variance': variance,
                    'predecessors': activity['predecessors'],
                    'resource': 'Default'
                }
                formatted_activities.append(formatted_activity)
            
            # Run the analysis using expected times
            graph, critical_paths, critical_activities, project_stats = analyzer.analyze_with_uncertainty(formatted_activities)
            
            # Calculate probability if target duration provided
            probability = None
            if target_duration and project_stats:
                project_mean = project_stats.get('mean_duration', 0)
                project_variance = project_stats.get('variance', 0)
                if project_variance > 0:
                    z_score = (target_duration - project_mean) / (project_variance ** 0.5)
                    # Use scipy if available, otherwise simple approximation
                    try:
                        from scipy.stats import norm
                        probability = norm.cdf(z_score)
                    except ImportError:
                        # Simple approximation for normal CDF
                        import math
                        probability = 0.5 * (1 + math.erf(z_score / math.sqrt(2)))
            
            # Format results
            results = {
                'analysis_type': 'pert',
                'project_duration_expected': project_stats.get('mean_duration', 0) if project_stats else 0,
                'project_variance': project_stats.get('variance', 0) if project_stats else 0,
                'project_standard_deviation': (project_stats.get('variance', 0) ** 0.5) if project_stats else 0,
                'critical_path': critical_paths[0] if critical_paths else [],
                'critical_activities': critical_activities,
                'target_duration': target_duration,
                'completion_probability': probability,
                'confidence_level': confidence_level,
                'activities': []
            }
            
            # Extract activity results
            for node in graph.nodes():
                node_data = graph.nodes[node]
                if 'activity_id' in node_data:
                    activity_result = {
                        'id': node_data.get('activity_id'),
                        'name': node_data.get('name', ''),
                        'optimistic_duration': node_data.get('optimistic_time', 0),
                        'most_likely_duration': node_data.get('most_likely_time', 0),
                        'pessimistic_duration': node_data.get('pessimistic_time', 0),
                        'expected_duration': node_data.get('expected_time', 0),
                        'variance': node_data.get('variance', 0),
                        'standard_deviation': (node_data.get('variance', 0) ** 0.5),
                        'earliest_start': node_data.get('earliest_start', 0),
                        'earliest_finish': node_data.get('earliest_finish', 0),
                        'latest_start': node_data.get('latest_start', 0),
                        'latest_finish': node_data.get('latest_finish', 0),
                        'total_float': node_data.get('total_float', 0),
                        'is_critical': node_data.get('activity_id') in critical_activities
                    }
                    results['activities'].append(activity_result)
            
            return results
        
        # Run in thread to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _pert_analysis)
    
    async def _run_rcps_analysis(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run RCPS analysis using existing RCPSAnalyzer."""
        activities_data = job_data["activities"]
        resource_limits = job_data["resource_limits"]
        
        def _rcps_analysis():
            """Synchronous RCPS analysis in thread."""
            # First, create a CPM analysis as base
            from ...core.cpm_analyzer import CPMAnalyzer
            base_analyzer = CPMAnalyzer()
            
            # Convert activities for CPM base analysis
            formatted_activities = []
            for activity in activities_data:
                formatted_activity = {
                    'id': activity['id'],
                    'name': activity['name'],
                    'duration': activity['duration'],
                    'predecessors': activity['predecessors'],
                    'resource': activity['resource'],
                    'resource_quantity': activity.get('resource_quantity', 1),
                    'cost': 0  # Default cost for RCPS
                }
                formatted_activities.append(formatted_activity)
            
            # Run base CPM analysis
            base_graph, _, _ = base_analyzer.analyze(formatted_activities)
            
            # Now run RCPS analysis
            # Note: This is a simplified RCPS implementation
            # The full RCPS would require more complex resource scheduling
            
            results = {
                'analysis_type': 'rcps',
                'resource_limits': resource_limits,
                'project_duration': max([base_graph.nodes[node].get('latest_finish', 0) 
                                       for node in base_graph.nodes() if 'latest_finish' in base_graph.nodes[node]]),
                'resource_utilization': {},
                'activities': []
            }
            
            # Calculate resource utilization
            for resource, limit in resource_limits.items():
                total_usage = sum(activity.get('resource_quantity', 1) 
                                for activity in activities_data 
                                if activity.get('resource') == resource)
                results['resource_utilization'][resource] = {
                    'limit': limit,
                    'total_required': total_usage,
                    'utilization_ratio': total_usage / limit if limit > 0 else float('inf')
                }
            
            # Extract activity results
            for node in base_graph.nodes():
                node_data = base_graph.nodes[node]
                if 'activity_id' in node_data:
                    # Find matching activity data
                    activity_data = next((a for a in activities_data 
                                        if a['id'] == node_data.get('activity_id')), {})
                    
                    activity_result = {
                        'id': node_data.get('activity_id'),
                        'name': node_data.get('name', ''),
                        'duration': node_data.get('duration', 0),
                        'resource': activity_data.get('resource', ''),
                        'resource_quantity': activity_data.get('resource_quantity', 1),
                        'earliest_start': node_data.get('earliest_start', 0),
                        'earliest_finish': node_data.get('earliest_finish', 0),
                        'latest_start': node_data.get('latest_start', 0),
                        'latest_finish': node_data.get('latest_finish', 0),
                        'total_float': node_data.get('total_float', 0)
                    }
                    results['activities'].append(activity_result)
            
            return results
        
        # Run in thread to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _rcps_analysis)
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a running job."""
        return self._running_jobs.get(job_id)
    
    def get_running_jobs_count(self) -> int:
        """Get the number of currently running jobs."""
        return len(self._running_jobs)
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job (if possible)."""
        if job_id in self._running_jobs:
            # For now, we can't cancel running jobs, but we can mark them
            # This would require more sophisticated job management
            logger.warning(f"Job cancellation requested for {job_id} but not implemented")
            return False
        return True


# Global analysis service instance
analysis_service = AnalysisService()


__all__ = ["AnalysisService", "analysis_service"]