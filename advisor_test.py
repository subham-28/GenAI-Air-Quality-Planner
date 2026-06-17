from services.advisor_service import get_air_quality_plan

result = get_air_quality_plan(
    city="Bhubaneswar",
    profile="Student",
    activity="Outdoor jogging",
    duration_minutes=30
)

print(result["recommendation"])
print(result["rag_explanation"])