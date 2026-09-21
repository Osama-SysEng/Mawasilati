abstract interface class LiveTrackingRepository {
  Future<List<Object>> load({String? cursor});
}
