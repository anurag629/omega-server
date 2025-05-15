from django.contrib import admin
from .models import AIProvider, Container, Script, Execution

@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider_type', 'is_active', 'priority')
    list_filter = ('provider_type', 'is_active')
    search_fields = ('name',)

@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'is_running', 'is_active', 'last_checked')
    list_filter = ('is_running', 'is_active')
    search_fields = ('name', 'image')
    
    actions = ['check_container_status']
    
    def check_container_status(self, request, queryset):
        from .agents.docker_agent import DockerAgent
        docker_agent = DockerAgent()
        
        updated = 0
        for container in queryset:
            is_running = docker_agent.check_container_status(container.name)
            if container.is_running != is_running:
                container.is_running = is_running
                container.save()
                updated += 1
        
        self.message_user(request, f"Updated status for {updated} containers.")
    
    check_container_status.short_description = "Check container running status"

@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'scene_class', 'provider', 'status', 'created_at')
    list_filter = ('status', 'provider')
    search_fields = ('id', 'scene_class', 'prompt')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    actions = ['execute_script']
    
    def execute_script(self, request, queryset):
        from .agents.execution_agent import ManimExecutionAgent
        execution_agent = ManimExecutionAgent()
        
        executed = 0
        for script in queryset:
            execution_agent.execute(script)
            executed += 1
        
        self.message_user(request, f"Execution triggered for {executed} scripts.")
    
    execute_script.short_description = "Execute selected scripts"

@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'script', 'attempt_number', 'is_successful', 'started_at', 'completed_at')
    list_filter = ('is_successful',)
    search_fields = ('id', 'script__id', 'error')
    readonly_fields = ('id', 'script', 'started_at', 'completed_at', 'original_script', 'modified_script')
