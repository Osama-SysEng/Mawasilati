class DriverConsoleState {
  const DriverConsoleState({this.loading = false, this.error, this.items = const []});
  final bool loading;
  final String? error;
  final List<Object> items;
}
