from rest_framework import viewsets, decorators, response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from . import selectors as sel, services as svc
from .permissions import IsProjectMemberOrReadOnly
from .serializers import (
    ClientSerializer,
    ProjectSerializer,
    TaskSerializer,
    TimeEntrySerializer,
    RegisterSerializer,
)
from .filters import ProjectFilter, TaskFilter, TimeEntryFilter
from .models import Project

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter # pyright: ignore[reportMissingImports]
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(["GET"])
def health(_request):
    return Response({"status": "ok"})

@extend_schema(summary="Register new user", tags=["Auth"], request=RegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": {"id": user.id, "username": user.username, "email": user.email},
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 

@extend_schema_view(
    list=extend_schema(summary="List clients", tags=["Clients"]),
    retrieve=extend_schema(summary="Get client", tags=["Clients"]),
    create=extend_schema(summary="Create client", tags=["Clients"]),
    update=extend_schema(summary="Update client", tags=["Clients"]),
    partial_update=extend_schema(summary="Patch client", tags=["Clients"]),
    destroy=extend_schema(summary="Delete client", tags=["Clients"]),
)
class ClientViewSet(viewsets.ModelViewSet):
    queryset = sel.clients_qs()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]

@extend_schema_view(
    list=extend_schema(summary="List projects", tags=["Projects"]),
    retrieve=extend_schema(summary="Get project", tags=["Projects"]),
    create=extend_schema(summary="Create project", tags=["Projects"]),
    update=extend_schema(summary="Update project", tags=["Projects"]),
    partial_update=extend_schema(summary="Patch project", tags=["Projects"]),
    destroy=extend_schema(summary="Delete project", tags=["Projects"]),
)
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = sel.projects_qs()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectFilter

@extend_schema_view(
    list=extend_schema(summary="List tasks", tags=["Tasks"]),
    retrieve=extend_schema(summary="Get task", tags=["Tasks"]),
    create=extend_schema(summary="Create task", tags=["Tasks"]),
    update=extend_schema(summary="Update task", tags=["Tasks"]),
    partial_update=extend_schema(summary="Patch task", tags=["Tasks"]),
    destroy=extend_schema(summary="Delete task", tags=["Tasks"]),
)
class TaskViewSet(viewsets.ModelViewSet):
    queryset = sel.tasks_qs()
    serializer_class = TaskSerializer
    permission_classes = [IsProjectMemberOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def perform_create(self, serializer):
        data = serializer.validated_data
        project: Project = data["project"]
        assignee = data.get("assignee")
        instance = svc.create_task(project=project, title=data["title"], assignee=assignee,
                                   description=data.get("description"),
                                   status=data.get("status","todo"),
                                   estimate_hours=data.get("estimate_hours",0),
                                   due_date=data.get("due_date"))
        serializer.instance = instance

@extend_schema_view(
    list=extend_schema(summary="List time entries", tags=["TimeEntries"]),
    retrieve=extend_schema(summary="Get time entry", tags=["TimeEntries"]),
    create=extend_schema(summary="Create time entry", tags=["TimeEntries"]),
    update=extend_schema(summary="Update time entry", tags=["TimeEntries"]),
    partial_update=extend_schema(summary="Patch time entry", tags=["TimeEntries"]),
    destroy=extend_schema(summary="Delete time entry", tags=["TimeEntries"]),
)
class TimeEntryViewSet(viewsets.ModelViewSet):
    queryset = sel.time_entries_qs()
    serializer_class = TimeEntrySerializer
    permission_classes = [IsProjectMemberOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TimeEntryFilter

    @extend_schema(
        summary="Report: total hours by project",
        tags=["Reports"],
        parameters=[
            OpenApiParameter(name="date_from", required=False, location=OpenApiParameter.QUERY, description="YYYY-MM-DD"),
            OpenApiParameter(name="date_to", required=False, location=OpenApiParameter.QUERY, description="YYYY-MM-DD"),
        ],
        responses={200: None},
    )
    @decorators.action(detail=False, methods=["get"], url_path="report/by-project")
    def report_by_project(self, request):
        df = request.query_params.get("date_from")
        dt = request.query_params.get("date_to")
        return response.Response(list(sel.total_hours_by_project(df, dt)))
