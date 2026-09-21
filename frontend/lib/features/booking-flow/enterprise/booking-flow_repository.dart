abstract interface class BookingFlowRepository {
  Future<List<Object>> load({String? cursor});
}
