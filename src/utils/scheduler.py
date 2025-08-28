"""
Scheduler Module
Handles scheduled updates and manual triggers for dynamic knowledge
"""

import time
import logging
import threading
from typing import Callable, Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from src.config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScheduledTask:
    """Scheduled task data structure"""
    name: str
    function: Callable
    interval: int  # seconds
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True
    max_retries: int = 3
    retry_count: int = 0

class KnowledgeScheduler:
    """Scheduler for dynamic knowledge updates"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.scheduler_thread = None
        self.is_running = False
        self.update_callbacks: List[Callable] = []
        
        # Initialize default tasks
        self._initialize_default_tasks()
    
    def _initialize_default_tasks(self):
        """Initialize default scheduled tasks"""
        # Hourly knowledge update task
        self.add_task(
            name="hourly_knowledge_update",
            function=self._hourly_update,
            interval=config.DYNAMIC_UPDATE_INTERVAL,
            enabled=True
        )
        
        # Daily cleanup task
        self.add_task(
            name="daily_cleanup",
            function=self._daily_cleanup,
            interval=86400,  # 24 hours
            enabled=True
        )
        
        # Weekly learning analysis
        self.add_task(
            name="weekly_learning_analysis",
            function=self._weekly_learning_analysis,
            interval=604800,  # 7 days
            enabled=True
        )
    
    def add_task(self, name: str, function: Callable, interval: int, 
                 enabled: bool = True, max_retries: int = 3) -> bool:
        """Add a new scheduled task"""
        try:
            if name in self.tasks:
                logger.warning(f"Task '{name}' already exists, updating...")
            
            task = ScheduledTask(
                name=name,
                function=function,
                interval=interval,
                enabled=enabled,
                max_retries=max_retries
            )
            
            # Calculate next run time
            task.next_run = datetime.now() + timedelta(seconds=interval)
            
            self.tasks[name] = task
            logger.info(f"Added scheduled task: {name} (interval: {interval}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error adding task '{name}': {e}")
            return False
    
    def remove_task(self, name: str) -> bool:
        """Remove a scheduled task"""
        try:
            if name in self.tasks:
                del self.tasks[name]
                logger.info(f"Removed scheduled task: {name}")
                return True
            else:
                logger.warning(f"Task '{name}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Error removing task '{name}': {e}")
            return False
    
    def enable_task(self, name: str) -> bool:
        """Enable a scheduled task"""
        try:
            if name in self.tasks:
                self.tasks[name].enabled = True
                logger.info(f"Enabled scheduled task: {name}")
                return True
            else:
                logger.warning(f"Task '{name}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Error enabling task '{name}': {e}")
            return False
    
    def disable_task(self, name: str) -> bool:
        """Disable a scheduled task"""
        try:
            if name in self.tasks:
                self.tasks[name].enabled = False
                logger.info(f"Disabled scheduled task: {name}")
                return True
            else:
                logger.warning(f"Task '{name}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Error disabling task '{name}': {e}")
            return False
    
    def start_scheduler(self):
        """Start the scheduler thread"""
        if not self.is_running:
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            logger.info("Knowledge scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler thread"""
        self.is_running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
            logger.info("Knowledge scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Check each task
                for task_name, task in self.tasks.items():
                    if (task.enabled and task.next_run and 
                        current_time >= task.next_run):
                        
                        # Execute task
                        self._execute_task(task)
                
                # Sleep for a short interval
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        try:
            logger.info(f"Executing scheduled task: {task.name}")
            
            # Execute the task function
            result = task.function()
            
            # Update task timing
            task.last_run = datetime.now()
            task.next_run = datetime.now() + timedelta(seconds=task.interval)
            task.retry_count = 0  # Reset retry count on success
            
            logger.info(f"Task '{task.name}' completed successfully")
            
            # Notify callbacks
            self._notify_update_callbacks(task.name, result)
            
        except Exception as e:
            logger.error(f"Error executing task '{task.name}': {e}")
            task.retry_count += 1
            
            # Handle retries
            if task.retry_count < task.max_retries:
                # Schedule retry in 5 minutes
                task.next_run = datetime.now() + timedelta(minutes=5)
                logger.info(f"Task '{task.name}' scheduled for retry in 5 minutes")
            else:
                # Disable task after max retries
                task.enabled = False
                logger.error(f"Task '{task.name}' disabled after {task.max_retries} failed attempts")
    
    def add_update_callback(self, callback: Callable):
        """Add a callback function to be called when tasks complete"""
        self.update_callbacks.append(callback)
        logger.info(f"Added update callback: {callback.__name__}")
    
    def remove_update_callback(self, callback: Callable):
        """Remove an update callback"""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
            logger.info(f"Removed update callback: {callback.__name__}")
    
    def _notify_update_callbacks(self, task_name: str, result: Any):
        """Notify all update callbacks"""
        for callback in self.update_callbacks:
            try:
                callback(task_name, result)
            except Exception as e:
                logger.error(f"Error in update callback {callback.__name__}: {e}")
    
    def trigger_task_now(self, task_name: str) -> bool:
        """Trigger a task to run immediately"""
        try:
            if task_name in self.tasks:
                task = self.tasks[task_name]
                logger.info(f"Manually triggering task: {task_name}")
                
                # Execute immediately
                self._execute_task(task)
                return True
            else:
                logger.warning(f"Task '{task_name}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Error triggering task '{task_name}': {e}")
            return False
    
    def get_task_status(self, task_name: str = None) -> Dict[str, Any]:
        """Get status of scheduled tasks"""
        try:
            if task_name:
                # Get specific task status
                if task_name in self.tasks:
                    task = self.tasks[task_name]
                    return {
                        "name": task.name,
                        "enabled": task.enabled,
                        "interval": task.interval,
                        "last_run": task.last_run.isoformat() if task.last_run else None,
                        "next_run": task.next_run.isoformat() if task.next_run else None,
                        "retry_count": task.retry_count,
                        "max_retries": task.max_retries
                    }
                else:
                    return {"error": f"Task '{task_name}' not found"}
            else:
                # Get all tasks status
                status = {
                    "scheduler_running": self.is_running,
                    "total_tasks": len(self.tasks),
                    "enabled_tasks": sum(1 for t in self.tasks.values() if t.enabled),
                    "tasks": {}
                }
                
                for name, task in self.tasks.items():
                    status["tasks"][name] = {
                        "enabled": task.enabled,
                        "interval": task.interval,
                        "last_run": task.last_run.isoformat() if task.last_run else None,
                        "next_run": task.next_run.isoformat() if task.next_run else None,
                        "retry_count": task.retry_count
                    }
                
                return status
                
        except Exception as e:
            logger.error(f"Error getting task status: {e}")
            return {"error": str(e)}
    
    def get_next_run_time(self) -> Optional[datetime]:
        """Get the next scheduled run time for any task"""
        try:
            next_runs = []
            for task in self.tasks.values():
                if task.enabled and task.next_run:
                    next_runs.append(task.next_run)
            
            if next_runs:
                return min(next_runs)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting next run time: {e}")
            return None
    
    # Default task functions
    def _hourly_update(self):
        """Default hourly knowledge update task"""
        try:
            # This will be replaced by the actual update function
            # when the scheduler is connected to the knowledge manager
            logger.info("Hourly knowledge update task executed")
            return {"status": "success", "message": "Hourly update completed"}
        except Exception as e:
            logger.error(f"Error in hourly update task: {e}")
            return {"status": "error", "message": str(e)}
    
    def _daily_cleanup(self):
        """Default daily cleanup task"""
        try:
            logger.info("Daily cleanup task executed")
            return {"status": "success", "message": "Daily cleanup completed"}
        except Exception as e:
            logger.error(f"Error in daily cleanup task: {e}")
            return {"status": "error", "message": str(e)}
    
    def _weekly_learning_analysis(self):
        """Default weekly learning analysis task"""
        try:
            logger.info("Weekly learning analysis task executed")
            return {"status": "success", "message": "Weekly learning analysis completed"}
        except Exception as e:
            logger.error(f"Error in weekly learning analysis task: {e}")
            return {"status": "error", "message": str(e)}
    
    def connect_knowledge_manager(self, knowledge_manager):
        """Connect the scheduler to a knowledge manager"""
        try:
            # Replace default task functions with actual knowledge manager methods
            if hasattr(knowledge_manager, 'force_update'):
                self.tasks["hourly_knowledge_update"].function = knowledge_manager.force_update
            
            if hasattr(knowledge_manager, 'cleanup_old_data'):
                self.tasks["daily_cleanup"].function = lambda: knowledge_manager.cleanup_old_data()
            
            # Add update callback to notify knowledge manager
            self.add_update_callback(knowledge_manager._on_scheduled_update)
            
            logger.info("Scheduler connected to knowledge manager")
            
        except Exception as e:
            logger.error(f"Error connecting scheduler to knowledge manager: {e}")
    
    def shutdown(self):
        """Clean shutdown of the scheduler"""
        try:
            self.stop_scheduler()
            logger.info("Knowledge scheduler shutdown complete")
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}")

# Global scheduler instance
scheduler = KnowledgeScheduler()

def get_scheduler() -> KnowledgeScheduler:
    """Get the global scheduler instance"""
    return scheduler 