abstract interface class DriverConsoleRepository {
  Future<List<Object>> load({String? cursor});
}
