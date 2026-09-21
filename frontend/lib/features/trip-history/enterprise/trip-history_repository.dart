abstract interface class TripHistoryRepository {
  Future<List<Object>> load({String? cursor});
}
