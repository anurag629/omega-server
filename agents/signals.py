from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Script, Execution
from .agents.execution_agent import ManimExecutionAgent

@receiver(post_save, sender=Script)
def execute_new_script(sender, instance, created, **kwargs):
    """
    Automatically execute newly created scripts if auto_execute flag is set
    """
    # Check if this is a new script with auto_execute flag
    if created and getattr(instance, 'auto_execute', False):
        # Create execution agent
        execution_agent = ManimExecutionAgent()
        
        # Execute script asynchronously (in a separate thread)
        # In a real production environment, this should use a task queue like Celery
        import threading
        execution_thread = threading.Thread(
            target=execution_agent.execute,
            args=(instance,),
            kwargs={'max_attempts': 100}
        )
        execution_thread.daemon = True
        execution_thread.start()

@receiver(post_save, sender=Execution)
def notify_execution_complete(sender, instance, created, **kwargs):
    """
    Handle notifications when an execution is completed
    """
    # Skip if this is a new execution being created
    if created:
        return
        
    # Check if this is a completed execution (has completed_at set)
    if instance.completed_at and instance.script:
        pass
        # Here you could add code to:
        # 1. Send notifications (email, websocket, etc.)
        # 2. Update related models
        # 3. Trigger other workflows
        
        # Example: Update script.latest_execution reference if you add that field 