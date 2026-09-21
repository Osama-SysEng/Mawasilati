abstract interface class JourneyPlannerRepository {
  Future<List<Object>> load({String? cursor});
}
