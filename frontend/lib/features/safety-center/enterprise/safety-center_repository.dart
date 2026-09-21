abstract interface class SafetyCenterRepository {
  Future<List<Object>> load({String? cursor});
}
